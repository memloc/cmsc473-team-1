import sys
import pathlib
import datetime
import subprocess

usage="""
python run.py {FLAGS}
FLAGS:
  -q             Run quiet. Spawned process will write to a log file rather than
                 to stderr/stdout.
"""

if __name__ == "__main__":
    print(usage)
    shutdown = False
    timestamp = datetime.datetime.now().strftime('%y%m%d%H%M%S')
    logs_path = pathlib.Path("./logs/")
    logs_path.mkdir(exist_ok=True)
    log = pathlib.Path(f"./logs/{timestamp}.log")

    # Launch server.py process, have it write stdout/stdder to a log file
    if not "-q" in sys.argv:
        proc_flask = subprocess.Popen(['python', 'server.py'],)
    else:
        proc_flask = subprocess.Popen(
            ['python', 'server.py'],
            stdout=open(log.absolute(), "w+"),
            stderr=subprocess.STDOUT
        )

    if proc_flask.poll() != None:
        print("Failed to start server.py")
        shutdown=True

    if not shutdown:
        print("Flask running on http://127.0.0.1:8080")

    # Run until either server.py or model.py terminates, or user wants terminate
    while not shutdown:
        cin = input("Terminate [y/n]: ")
        if cin == "y":
            shutdown=True
        if proc_flask.poll() != None:
            shutdown = True
        
    if proc_flask.poll() == None:
        proc_flask.terminate()
        # Force kill if process wont end
        if proc_flask.poll() != None:
            proc_flask.kill()

    if log.exists():
        print(f"Flask terminated see log for details: {log}")
