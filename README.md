# cmsc473-team-1

## Requirements
Ollama: https://ollama.com/download

## Setup Instructions
Using `pyenv` or `conda` create a virtual python environment with python version 3.10 and install the required packages
```
conda create -n nlp python==3.10
conda activate nlp
pip install -r requirements.txt
```

## Running
*NOTE:* If the ollama models are not preinstalled this command will require additional initialization time in order to download the ollama models, before starting the webserver.

To start the webserver with the 4b models on localhost:8080 run the following command
```
python run.py -m 4b
```

To start the webserver with the 8b models on localhost:8080 run the following command
```
python run.py -m 8b
```

For help, run 
```
python run.py -h 
```

A video of the full installation process can be seen [here](https://drive.google.com/file/d/17HEIthqF2pAYSxjOGg9t5WFw29sDYE6I/view?usp=sharing).

