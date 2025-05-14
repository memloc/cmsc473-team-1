import time
import hashlib
import datetime
import threading
import asyncio
import model
import random

from flask import Flask, render_template, request
app = Flask(__name__)
sessions = {}              # Primary key is session_id, verified sessions
tasks = {}                 # Primary key is session_id, tasks of verified sessions
TASK_WAITING="waiting"     # Task is in queue but not active.
TASK_ACTIVE="active"       # Task is being worked on
TASK_COMPLETED="completed" # Task finished and (needs to be collected)
TASK_FAILED="failed"       # Task failed and (needs to be collected / removed)


class Session:
    def __init__(self):
        # Create a session for the client to track their id and active jobs
        self.ts = datetime.datetime.now().strftime('%y%m%d%H%M%S')
        self.id = hashlib.blake2b(self.ts.encode('utf-8'),digest_size=8).hexdigest()

class Task:
    def __init__(self, session_id, document, human_summary):
        self.session_id = session_id
        self.status = TASK_WAITING # Not started, but waiting 
        self.time_created = time.time() # Used to determine which task to take 
        self.document = document
        self.human_summary = human_summary
        self.results = []


# Handle front-end request for model evaluation status 
def handle_req_status(session_id):
    if session_id not in tasks.keys():
        return { 'status': 'error', 'error': f'Task for "{session_id}" does not exist.' }
    task_status = tasks[session_id].status
    return { 'status': task_status }


# Handle front-end request for document model evaluation
def handle_req_evaluate(session_id, document, human_summary):
    if session_id in tasks.keys():
        return {'status': 'error', 'error': 'Client task already exists.'}
    # Create a new task task and return the status (WAITING)
    tasks[session_id] = Task(session_id,document,human_summary)
    return {'status': tasks[session_id].status }


# Handle front-end request for model evaluation results
def handle_req_results(session_id):
    if session_id not in tasks.keys():
        return {'status': 'error', 'error': f'No task for "{session_id}" exists.'}
    if tasks[session_id].status not in [TASK_FAILED, TASK_COMPLETED]:
        return {'status': 'error', 'error': 'Task not ready to be collected.'}
    # Remove the task from the tasks dict, and return the results
    task = tasks.pop(session_id)
    return { 'status': 'success', 'results': task.results }

# Handle front-end request for a random document/summary pair from the dataset
def handle_req_dataset_example():
    idx_sample = random.randint(0, len(model.ds['train']))
    doc = model.ds['train'][idx_sample]['document']
    human_summary = model.ds['train'][idx_sample]['summary']
    return {'status': 'success', 'example': { 'document': doc, 'human_summary': human_summary } }


# Example of valid requests:
# {'session_id': id, 'request': {'type': 'status'} }
# {'session_id': id, 'request': {'type': 'evaluate', 'document': '', human_summary: ''}}
# {'session_id': id, 'request': {'type': 'results'} }
# {'session_id': id, 'request': {'type': 'dataset_example'} }
@app.route('/request', methods=["POST", "GET"])
def handle_requests():
    try:
        msg = request.get_json()
        session_id = msg['session_id']
        req_type = msg['request']['type']
        # Tell the client they are not recognized (must refresh browser window)
        if session_id not in sessions.keys():
            return {'status': 'error', 'error': 'Session id is not recognized. Refresh page.'}
        # Handle the request from the client
        if req_type == "status":
            return handle_req_status(session_id)
        if req_type == "evaluate":
            try:
                document = msg['request']['document']
                human_summary = msg['request']['human_summary']
                return handle_req_evaluate(session_id, document, human_summary)
            except Exception as e:
                raise e
        if req_type == "results":
            return handle_req_results(session_id)
        if req_type == "dataset_example":
            return handle_req_dataset_example()
    except Exception as e:
        return {'status': 'error', 'origin': 'handle_requests()' }
    
    
@app.route('/', methods=['POST', 'GET'])
def entry():
    # Assign the user with a session to handle their requests
    session = Session()
    sessions[session.id] = session
    return render_template("index.html", session_id=session.id)


# Manages enqueing, starting, updating and removing tasks
async def task_service():
    while True:
        # Select the next task to run
        next_task_id = ""
        for task_id in tasks.keys():
            # A queue would be better for this
            if tasks[task_id].status == TASK_WAITING:
                if next_task_id == "":
                    next_task_id = task_id
                elif tasks[task_id].time_created < tasks[next_task_id].time_created:
                    next_task_id = task_id

        # If no task was found, sleep for a little then search again
        task_id = next_task_id
        if task_id == "":
            time.sleep(5)
            continue

        # Evaluate the selected task and store the results in tasks
        tasks[task_id].status = TASK_ACTIVE
        # See model.py
        tasks[task_id].results = await model.evaluate(tasks[task_id].document,tasks[task_id].human_summary) 
        tasks[task_id].status = TASK_COMPLETED


def launch_async_task_service():
    # NOTE: Cannot directly call asyncio.run in another thread need to setup 
    # event loop.
    # https://debuglab.net/2024/03/19/how-do-i-pass-an-async-function-to-a-thread-target-in-python/
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(task_service()) 


def main():
    # TODO: shutdown safely...
    task_service_thread = threading.Thread(target=launch_async_task_service)
    task_service_thread.start()
    app.run(host="127.0.0.1", port=8080)
    task_service_thread.join()
