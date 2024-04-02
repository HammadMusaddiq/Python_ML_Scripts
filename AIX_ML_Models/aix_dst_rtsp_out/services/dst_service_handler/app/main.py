from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import docker
import os

HOST_IP = os.getenv("SYSTEM_IP", "")
resources_volume = os.getenv("LOCAL_RESOURCES_DIR", None)
node_ip_ftp = os.getenv("node_ip_ftp", "")
node_port_ftp = os.getenv("node_port_ftp", "")
node_path_ftp = os.getenv("node_path_ftp", "")
auth_user_ftp = os.getenv("auth_user_ftp", "")
auth_pass_ftp = os.getenv("auth_pass_ftp", "")
             
COUNT = 1

client = docker.from_env()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def index():
    return {"message": "DST Service Handler API is working..."}


@app.get("/images_list")
async def image_list():
    return {
        "images": [
        docker_img.tags[0] 
        for docker_img in client.images.list() 
        if len(docker_img.tags) > 0
        ]
    }

@app.post("/run_realtime")
async def run_realtime(
    camera_url: str = "",
    camera_ip: str = "",
    kafka_ip: str = "",
    out_port: int = None,
    threats: str = "", 
    name: str = "",
    lat: str = "",
    lng: str = "",
    sink_port: int = None
):  
    stream_url = ""
    container_id = ""
    status_code = ""
    error = ""

    global HOST_IP, COUNT, resources_volume, node_ip_ftp, node_port_ftp,\
        node_path_ftp, auth_user_ftp, auth_pass_ftp

    try:
        ul1 = docker.types.Ulimit(name="memlock", soft=-1, hard=-1)
        ul2 = docker.types.Ulimit(name="stack", soft=67108864, hard=67108864)
        ulimits = [ul1, ul2]
        run_command = f"python3 /app/dst_multistream_app.py --input '{camera_url}' --ip '{camera_ip}' --kafka '{kafka_ip}'\
        --out {out_port} --threats {threats} --name '{name}' --lat '{lat}' --long '{lng}' --sport {sink_port}"
        
        print(f"Running following command: {run_command}")

        
        if resources_volume is None or not resources_volume.startswith("/"):
            return {
                "status": 500,
                "message": f"**{resources_volume}** must be an absolute path"
            }

        cti = client.containers.run(
            image="dst_rtsp_out_multi",
            # name = "dst_rtsp_out_multi_{}".format(int(COUNT)), 
            command=run_command,
            restart_policy={'Name': 'always'},
            auto_remove=False, # True | False out_port
            detach=True,
            ipc_mode="host",
            ulimits=ulimits,
            runtime="nvidia",
            ports={ 
                f"{out_port}": out_port 
            }, 
            environment={
                'TZ': 'Asia/Karachi',
                'node_ip_ftp': node_ip_ftp,
                'node_port_ftp': node_port_ftp,
                'node_path_ftp': node_path_ftp,
                'auth_user_ftp': auth_user_ftp,
                'auth_pass_ftp': auth_pass_ftp
            }, 
            volumes={
            resources_volume :{
                "bind": "/resources",
                "mode": "rw",
                }
            },
        )
        
        status_code = 200
        container_id = str(cti.id)
        stream_url = "rtsp://{}:{}/ds-aix".format(str(HOST_IP),out_port)
        error = ""
        COUNT += 1


    except Exception as E:
        status_code = 500,
        error = str(E)

    return {
        "status_code": status_code,
        "rts_port": out_port,
        "container_id": container_id,
        "stream_url" : stream_url,
        "error" : error
    }

@app.post("/stop_realtime")
async def stop_realtime(
    container_id: str = None,
    rts_port: int = None,
):
    api_client = client.api
    api_client.stop(container_id)

    return {
        "success": 200
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8096)
