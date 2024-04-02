import socketio
from kafka import KafkaConsumer
from json import loads
import uvicorn
import multiprocessing
import queue

background_task_started = False

# Initialize the SocketIO extension
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(sio)
message_queue = multiprocessing.Queue()


def consumer_process(queue):
    consumer = KafkaConsumer(
        "streamDetections",
        bootstrap_servers=["localhost:29092"],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="my-group",
        value_deserializer=lambda x: loads(x.decode("utf-8")),
    )

    for msg in consumer:
        queue.put(msg.value)


# Start a background task to emit events to connected clients


async def background_thread_consumer():
    consumer_process_p = multiprocessing.Process(
        target=consumer_process, args=(message_queue,)
    )
    consumer_process_p.start()

    while True:
        try:
            message = message_queue.get(timeout=1)
            await sio.emit("detect_event", {"data": message})
            await sio.sleep(0.02)
        except queue.Empty:
            await sio.sleep(0.02)


@sio.on("connect")
async def connect(sid, environ):
    print(f"Client {sid} connected")
    global background_task_started
    if not background_task_started:
        # sio.start_background_task(read_data)
        sio.start_background_task(background_thread_consumer)
        background_task_started = True


if __name__ == "__main__":
    print(f"Service Started Succefully")
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
