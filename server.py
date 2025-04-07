import time
import ollama
from datasets import load_dataset
from flask import Flask, render_template

app = Flask(__name__)
ds = load_dataset("alexfabbri/multi_news")
ollama_model_names = [
    "dolphin3",             # 8b params, 128k context length
    "deepseek-r1:8b",       # 8b params, 131k context length
    "llama3.1:8b",          # 8b params, 131k context length
    "granite3.1-dense:8b"   # 8b params, 131k context length
]

@app.route('/')
def entry():
    # Just print the available models for now
    models = available_models_string = ollama.list().dict()
    return render_template("index.html", models=available_models_string)

def pull_models():
    # Pull the models from ollama
    start_time = time.time()
    for model in ollama_model_names:
        elapsed = time.time() - start_time
        print(f"({elapsed:.2}): Pulling model '{model}' from ollama")
        ollama.pull(model)
    return


if __name__ == "__main__":
    # Ensure all models are downloaded before starting the webserver
    pull_models()
    app.run(host="127.0.0.1", port=8080, debug=True)
