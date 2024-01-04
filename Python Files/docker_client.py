import docker
import os, sys

client = docker.from_env()

ul1 = docker.types.Ulimit(name="memlock", soft=-1, hard=-1)
ul2 = docker.types.Ulimit(name="stack", soft=67108864, hard=67108864)
ulimits = [ul1, ul2]
out_port = 8008

run_command = f"python3 /app/test.py"

print(f"Running following command: {run_command}")

# Set the path to the Python file and the app directory in the container
python_file = "/home/hammad/Downloads/Python Files/test.py"
host_directory = os.path.dirname(python_file)
app_directory = "/app"

cti = client.containers.run(
    # image="python",
    image="b26eb5f12b4e",
    name="test_container",
    command=run_command, # python script with sleep timer
    auto_remove=False, # True | False (Not kill container after container’s process exits)
    detach=True,
    ipc_mode="host",
    ulimits=ulimits,
    # runtime="nvidia",
    ports={ 
        f"{out_port}": out_port 
    },  
    volumes={host_directory: {"bind": app_directory, "mode": "rw"}},
)

# cti = client.containers.run("b26eb5f12b4e", name="test_container", stdin_open = True, tty = True, detach=True)
# cti = container = client.containers.run('bfirsh/reticulate-splines',detach=True)

print(cti)
print(cti.id)

