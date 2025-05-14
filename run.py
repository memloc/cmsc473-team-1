import time
import datetime
import pathlib
import argparse
import threading
import model
import server

def pull_models(ollama_model_names):
    start_time = time.time()
    for model_name in ollama_model_names:
        elapsed = time.time() - start_time
        print(f"({elapsed:.2}): Pulling model '{model_name}' from ollama")
        model.ollama.pull(model_name)

if __name__ == "__main__":
    shutdown = False

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--models', help="Select the group of models (3b/3b or 8b) to use during runtime.", choices=["4b", "8b"], required=True, default="4b")
    # parser.add_argument('-q', '--quiet', help="Run quiet and write to a log file rather than to stderr/stdout.")

    args = parser.parse_args()

    if args.models == "4b":
        model.ollama_model_names = [
            "qwen3:4b",   # 4b params, 40k context length
            "phi3.5:3.8b",# 4b params, 131k context length
            "cogito:3b",  # 3b params, 131k context length
            "gemma3:4b",  # 4b params, 131k context length
        ]
        model.summarizer_models = model.ollama_model_names[0:3]
        model.grader_model = model.ollama_model_names[-1]

        
    elif args.models == "8b":
        model.ollama_model_names = [
            "dolphin3",             # 8b params, 128k context length
            "deepseek-r1:8b",       # 8b params, 131k context length
            "granite3.1-dense:8b"   # 8b params, 131k context length
            "llama3.1:8b",          # 8b params, 131k context length
        ]
        model.summarizer_models= model.ollama_model_names[0:2]
        model.grader_model = model.ollama_model_names[-1]

    pull_models(model.ollama_model_names)

    print(f"summarizers: {model.summarizer_models}")
    print(f"grader: {model.grader_model}")

    # Launch flask, have it write stdout/stdder to a log file
    server.main()
