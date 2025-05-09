import time
import asyncio
import logging
import ollama
from ollama import AsyncClient
from datasets import load_dataset
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Load the document dataset
ds = load_dataset("alexfabbri/multi_news")
# Set up ollama client and declare models
ollama_cli = AsyncClient()
ollama_model_names = [
    "dolphin3",             # 8b params, 128k context length
    "deepseek-r1:8b",       # 8b params, 131k context length
    "llama3.1:8b",          # 8b params, 131k context length
    "granite3.1-dense:8b"   # 8b params, 131k context length
]

def pull_models():
    # Pull the models from ollama
    start_time = time.time()
    for model in ollama_model_names:
        elapsed = time.time() - start_time
        print(f"({elapsed:.2}): Pulling model '{model}' from ollama")
        ollama.pull(model)
    return

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


# Run the task generate summaries, performs comparisons, calcs metrics and evaluation
async def evaluate(document, human_summary):
    # Generate model summaries
    outputs = await query_all_models(
        ollama_model_names,
        f"Summarize the following document in a single paragraph:\n{document}"
    )
    # Make all other models assess the quality of each other against the human summary
    # for model_idx in range(len(outputs)):
    #     current_model_name = outputs[model_idx].model
    #     current_model_summary = outputs[model_idx].message.content
    #     # Calculating similarity compared to human summary
    #     similarity_score = calculate_similarity(current_model_summary, summary)
    #     print(f"{current_model_name} Similarity to human summary: {similarity_score}")
    #     assessments = await query_all_models(
    #         [name for name in ollama_model_names if name != current_model_name ],
    #         f"Compare {current_model_summary} and {summary}",
    #     )
    # Just consider the model summaries as results (for testing)
    results = [x.message.content for x in outputs]
    return results
