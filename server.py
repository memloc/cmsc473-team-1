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
    models_available = ollama.list().dict()
    return render_template("index.html", models=models_available)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
