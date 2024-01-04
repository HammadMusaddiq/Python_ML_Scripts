from datetime import datetime
import time
import json
from kafka import KafkaProducer
from faker import Faker
import random

fake = Faker()


def json_serializer(data):
    return json.dumps(data).encode("utf-8")


def get_partitions(key, all, availaible):
    return 0  # for sending data to only partition 1


producer = KafkaProducer(bootstrap_servers=['10.100.102.101:6667'],
                         value_serializer=json_serializer,
                         # partitioner=get_partitions)
                         )

if __name__ == "__main__":


    video_urls = ["http://10.100.102.114/osint_system/media_files/MDS_Downloads/MDS_Video/164612544730664.mp4",\
                "http://10.100.102.114/osint_system/media_files/MDS_Downloads/MDS_Video/164615300108623.mp4",\
                "http://10.100.102.114/osint_system/media_files/MDS_Downloads/MDS_Video/164615287064955.mp4",\
                "http://10.100.102.114/osint_system/media_files/MDS_Downloads/MDS_Video/1646144280809036.mp4",\
                "http://10.100.102.114/osint_system/media_files/MDS_Downloads/MDS_Video/1646210380972676.mp4"]

    while True:

        url_count = random.randrange(0,3)

        if url_count == 0:
            video_url = []
        elif url_count == 1:
            video_url = [{'url':random.choice(video_urls)}]
        else:
            video_url = [{'url':random.choice(video_urls)},{'url':random.choice(video_urls)}]

        test = {
            'data_type': 'linkedin_user_posts',
            "target_information": {
                "target_type": "linkedin",
                "target_subtype": "user",
                "GTR": "st_tw_7784",
                "CTR": "2",
                "username": fake.name(),
                
            },
            "posts": {
                "author": {
                    "entity_type": "profile",
                    "name": fake.text(),
                    "username": fake.name(),
                    "url_c": "https://www.linkedin.com/in/kate-gould-599818201",
                    "image": "https://media-exp1.licdn.com/dms/image/C4E03AQFTL1JY2E1j-Q/profile-displayphoto-shrink_100_100/0/1624930127129?e=2147483647&v=beta&t=ZbDfvaYlMnlJmaZpHXPrWRKQ3fhLCvFO9DtQE1ckG50"
                },
                "url_c": "",
                "timestamp_c": datetime.now().second,
                "text_c": "\nI am beyond excited to share that I have accepted an internship with Slytrunk's software development team for Summer 2021. I am so grateful for this opportunity and look forward to working with such a great company.\n",
                "type": {
                    "is_picture": True,
                    "is_text": True,
                    "is_video": False,
                    "is_shared": False
                },
                "media_c":
                [fake.image_url()],

                "video": video_url,

                "shared_post": "null",

                "impressions": {
                    "no_of_reactions_c": 67,
                    "no_of_comments_c": 21
                },
                "reactions": {
                    "like": [

                    ],
                    "empathy": [

                    ],
                    "praise": [

                    ],
                    "appreciation": [

                    ],
                    "maybe": [

                    ],
                    "interest": [

                    ]
                },
                "comments": [
                    {
                        "commenter": {
                            "full_name": "Talia Yaakoby",
                            "username": "talia-yaakoby-b7a4081b7",
                            "url": "https://www.linkedin.com/in/talia-yaakoby-b7a4081b7",
                            "profile_image_url": "https://media-exp1.licdn.com/dms/image/C4D03AQGFime_eSJjNg/profile-displayphoto-shrink_100_100/0/1637248815082?e=1654128000&v=beta&t=aoRU9224w63YdtP9Rx0iGzLCuruHykRGh9fgLD0UeFo"
                        },
                        "text": fake.text(),
                        "picture_link": "",
                        "replies": [

                        ]
                    }
                ]
            }
        }

        # registered_user = get_registered_user()
        # print(registered_user)
        producer.send("testing_bds_stream", test)
        print("Running...")
        #print(test)
        time.sleep(4)
