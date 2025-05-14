import time
import asyncio
import logging
import ollama
import re
from ollama import AsyncClient
from datasets import load_dataset
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Dict

ollama_cli = AsyncClient()
global ollama_model_names
grader_model = ""
summarizer_models = []

# Load the document dataset
ds = load_dataset("alexfabbri/multi_news",trust_remote_code=True)


def create_grader_prompt(document, summary):
    prompt = (
        "Here is the human summary:\n\n"
        f"{document}\n\n"
        "Here is one model’s summary:\n\n"
        f"{summary}\n\n"
        "You are an expert evaluator. Compare the LLM–generated summary to the human reference summary and assign two subscores:"
        " 1. Accuracy (0.0–0.5): how faithfully the LLM summary reflects the reference content. "
        " 2. References (0.0–0.5): whether the LLM summary correctly cites its sources."
        " Compute the total score by summing these subscores (range 0.0–1.0). "
        "**Output ONLY the combined score as a decimal** (for example: `0.40`). Do **not** include any explanation, labels, or extra text."
    )
    return prompt


def create_summarizer_prompt(document):
    prompt = (
        "You are a summarizer. Your task is to summarize the following article. "
        "You should reference where you got the information from."
        "Here is an example of a summary:\n\n"
        "[Global average temperatures have increased by 1.1 °C since the late 19th century, driven largely by CO₂ emissions from burning fossil fuels [1]. Sea levels rose by 20 cm between 1901 and 2018, with an annual acceleration of 3.3 mm over the past two decades [2]. Without rapid decarbonization, models project a further 2–3 °C warming by 2100 under current policies [1,3]."
        "References: 1. IPCC, “Summary for Policymakers,” AR6 Climate Change 2021 Report, 2021. 2. NASA, “Sea Level Rise,” Earth Observatory, 2020. 3. UNEP, “Emissions Gap Report 2022,” United Nations Environment Programme, 2022.]"
        "Now, Please provide a concise summary of the following article:\n\n"
        f"{document}"
    )
    return prompt


def calculate_similarity(summary1, summary2):
    vectorizer = TfidfVectorizer()
    vector = vectorizer.fit_transform([summary1, summary2])
    similarity_matrix = cosine_similarity(vector)
    similarity_score = similarity_matrix[0, 1]
    logging.log(1, f"similarity score {similarity_score}")
    return similarity_score


async def query_model(model, prompt):
    messages = [{'role': 'user', 'content': prompt }]
    logging.log(1, msg=f"Sent prompt to: {model}")
    response = await ollama_cli.chat(model=model, messages=messages)
    return response


async def query_all_models(models, prompt):
    tasks = [query_model(model, prompt) for model in models]
    results = await asyncio.gather(*tasks)
    return results



async def grade(article: str, summaries: Dict[str, str]) -> Dict[str, str]:
    grades = {}
    for model, summary in summaries.items():
        grader_prompt = create_grader_prompt(article,summary)
        resp = await query_model(grader_model, prompt=grader_prompt)
        print(resp.message.content)
        m = re.search(r'([0-1]\.\d{1,2})', resp.message.content)
        score = m.group(1) if m else None
        text_sim = calculate_similarity(article, summary)
        print(score)
        print(text_sim)
        avg_score = (float(score) + text_sim) / 2 if score else None
        if avg_score is not None:
            round_avg_score = round(avg_score, 2)
            final = float(round_avg_score)
            grades[model] = final
        else:
            None
    return grades



# Run the task generate summaries, performs comparisons, calcs metrics and evaluation
async def evaluate(document, human_summary):
    # Generate model summaries
    summarizer_responses = await query_all_models(
        summarizer_models,
        create_summarizer_prompt(document)
    )

    # Remove the thought text from deepseek
    format_message = lambda model, message: \
        message if model not in ["deepseek-r1:8b", "qwen3:4b"] \
            else message.split('<think>')[0] + message.split('</think>')[1]

    summaries = {}
    for resp in summarizer_responses:
        summaries[resp.model] = format_message(resp.model, resp.message.content)

    print(summaries)

    grades = await grade(document, summaries)

    results = []
    for model in grades.keys():
        x = {"label": model, "value": grades[model] }
        print(x)
        results.append(x)
    print(results)
        
    # e.g.
    #[{"label": "Granite", "value": .73},
    # {"label": "Dolphin", "value": .64},
    # {"label": "Deepseek", "value": .39}]
    return results
