import time
import asyncio
import logging
import ollama
from ollama import AsyncClient
from datasets import load_dataset

ds = load_dataset("alexfabbri/multi_news")
ollama_cli = AsyncClient()
ollama_model_names = [
    "dolphin3",             # 8b params, 128k context length
    "deepseek-r1:8b",       # 8b params, 131k context length
    "llama3.1:8b",          # 8b params, 131k context length
    "granite3.1-dense:8b"   # 8b params, 131k context length
]

async def query_model(model, prompt):
    # global g_message_queue
    messages = [{'role': 'user', 'content': prompt }]
    logging.log(1, msg=f"Sent prompt to: {model}")
    response = await ollama_cli.chat(model=model, messages=messages)
    return response

async def query_all_models(models, prompt):
    tasks = [query_model(model, prompt) for model in models]
    results = await asyncio.gather(*tasks)
    return results

def pull_models():
    # Pull the models from ollama
    start_time = time.time()
    for model in ollama_model_names:
        elapsed = time.time() - start_time
        print(f"({elapsed:.2}): Pulling model '{model}' from ollama")
        ollama.pull(model)
    return
    
async def main():
    # Placeholder/test of async model querying and interaction
    ds_train = ds['train']
    for index in range(1):
        doc = ds_train[index]['document']
        summary = ds_train[index]['summary']
        outputs = await query_all_models(
            ollama_model_names,
            f"Summarize the following document in a single paragraph:\n{doc}"
        )
        # Make all other models assess the quality of each other against the human summary
        for model_idx in range(len(outputs)):
            current_model_name = outputs[model_idx].model
            current_model_summary = outputs[model_idx].message.content
            assessments = await query_all_models(
                [ name for name in ollama_model_names if name != current_model_name ],
                f"Compare {current_model_summary} and {summary}",
            )

if __name__ == '__main__':
    pull_models()
    asyncio.run(main())
