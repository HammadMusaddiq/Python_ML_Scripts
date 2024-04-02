import requests
import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv()
ELASTICSEARCH_HOST = os.getenv(
    "es_ip", "http://localhost:9200"
)  # Update the Elasticsearch host if needed
THRESHOLD = int(
    os.getenv("delete_esdata_thresh", "31")
)  # Update the memory threshold if needed
INDEX_PREFIX = "*streamdetections*"  # Update the index prefix if needed


def delete_old_indices():
    # Get all indices starting with INDEX_PREFIX
    r = requests.get(f"{ELASTICSEARCH_HOST}/_cat/indices/{INDEX_PREFIX}?h=index")
    if r.status_code != 200:
        print(f"Error getting indices: {r.content}")
        return

    indices = r.content.decode().split("\n")
    indices.remove("")
    # Sort indices by creation time
    indices = sorted(
        indices,
        key=lambda x: datetime.datetime.strptime(
            "_".join(x.split("_")[-3:]), "%Y_%m_%d"
        ),
        reverse=True,
    )

    total_size = 0
    for index in indices:
        # Get index size
        r = requests.get(f"{ELASTICSEARCH_HOST}/{index}/_stats/store")
        if r.status_code != 200:
            print(f"Error getting index stats: {r.content}")
            continue

        size_in_bytes = r.json()["_all"]["primaries"]["store"]["size_in_bytes"]
        size_in_gb = size_in_bytes / (1024**3)
        total_size += size_in_gb

        if total_size > THRESHOLD:
            # Delete the index if the total size exceeds the threshold
            r = requests.delete(f"{ELASTICSEARCH_HOST}/{index}")
            if r.status_code == 200:
                print(f"Deleted index {index}")
            else:
                print(f"Error deleting index {index}: {r.content}")
        else:
            print(f"Index {index} size: {size_in_gb} GB")


if __name__ == "__main__":
    while True:
        print("Service Started")
        delete_old_indices()
        time.sleep(1800)  # Run every half hour
