import schedule
import time
import json
from faker import Faker
from datetime import datetime
import random
fake = Faker()
def update_json():
    filename = 'my_file.json'
    listObj = []


    # Read JSON file
    with open(filename) as fp:
        listObj = json.load(fp)



    listObj.append({"posts": [
            {
                "categorization": {
                    "confidence": [
                        "0.40757415"
                    ],
                    "predictions": [
                        "the worldpost"
                    ]
                },
                "comments": [],
                "custom_categorization": {
                    "confidence": [
                        "0.9215194"
                    ],
                    "predictions": [
                        "anti-state"
                    ]
                },
                "data_type": "twitter_posts",
                "device_used": "Twitter Web App",
                "emotion": {
                    "confidence": [
                        "0.2403"
                    ],
                    "predictions": [
                        "neutral"
                    ]
                },
                "id": random.randint(0,3),
                "kafka_id": "e3140368-9846-42fa-8b17-007835d07143",
                "media_c": [],
                "retweet": False,
                "sentiment": {
                    "confidence": [
                        "0.4197"
                    ],
                    "predictions": [
                        "Positive"
                    ]
                },
                "tag_links": [],
                "tags": [],
                "text_c": "MESSAGE BY  H.E. THE  HIGH COMMISSIONER OF SRI LANKA IN PAKISTAN VICE ADMIRAL MOHAN WIJEWICKRAMA ON OCCASION OF THE 74th INDEPENDENCE DAY OF SRI LANKA",
                "timestamp_c": datetime.now().second,
                "topic": "sentiment_processed",
                "url_c": "",
                "video": [],
                "@timestamp": "2022-03-01T10:37:02.331+0500",
                "es_id": "VZ37Q38B9mWfogYvpnYg",
                "image": "",
                "is_verified": 0,
                "name": fake.text(),
                "username": fake.name(),
                "no_of_comments_c": "5",
                "no_of_quote_tweets": "0",
                "no_of_reactions_c": "22",
                "no_of_shares": "1",
                "like": [
                    {
                        "image": "https://pbs.twimg.com/profile_images/941688794302042112/YucY8fCr_normal.jpg",
                        "name": "Mubarak Cheema",
                        "url": "https://twitter.com/MubarakCheema2",
                        "username": "MubarakCheema2"
                    },
                    {
                        "image": "https://pbs.twimg.com/profile_images/586535938978750464/FHLi9ExI_normal.jpg",
                        "name": "Husnain Muzafar",
                        "url": "https://twitter.com/Husnain_muzafar",
                        "username": "Husnain_muzafar"
                    },
                    {
                        "image": "https://pbs.twimg.com/profile_images/1151841958857510913/kfsX0dWM_normal.jpg",
                        "name": "Dr.Mufti Akeel Pirzada",
                        "url": "https://twitter.com/muftiakeel",
                        "username": "muftiakeel"
                    },
                    {
                        "image": "https://pbs.twimg.com/profile_images/1487797638552559620/MfmKRcvT_normal.jpg",
                        "name": "Ezat Ullah",
                        "url": "https://twitter.com/EzatullahZakhil",
                        "username": "EzatullahZakhil"
                    },
                    {
                        "image": "https://pbs.twimg.com/profile_images/564386624377589761/MKLF7S4p_normal.jpeg",
                        "name": "Sharmeela Rassool",
                        "url": "https://twitter.com/Sha_Rassool",
                        "username": "Sha_Rassool"
                    },
                    {
                        "image": "https://pbs.twimg.com/profile_images/1489015267971805192/yLdOiyue_normal.jpg",
                        "name": "Tauseef Ahmed",
                        "url": "https://twitter.com/Tauseefahmed001",
                        "username": "Tauseefahmed001"
                    },
                    {
                        "image": "https://pbs.twimg.com/profile_images/1207890185830010880/vnMDr0-b_normal.jpg",
                        "name": "Waqas Butt",
                        "url": "https://twitter.com/Waqasbutt1990",
                        "username": "Waqasbutt1990"
                    },
                    {
                        "image": "https://pbs.twimg.com/profile_images/1472932303143845893/QWowB8CF_normal.jpg",
                        "name": "Mureed Hussain Keeryo",
                        "url": "https://twitter.com/MureedKeeryo",
                        "username": "MureedKeeryo"
                    },
                    {
                        "image": "https://pbs.twimg.com/profile_images/1390487046263824384/RfYr7eww_normal.jpg",
                        "name": "Mola Jatt",
                        "url": "https://twitter.com/MolaaJatt",
                        "username": "MolaaJatt"
                    },
                    {
                        "image": "https://pbs.twimg.com/profile_images/1420431988880814081/IiDijOR2_normal.jpg",
                        "name": "Muhammad Taqi",
                        "url": "https://twitter.com/TaqiSayz",
                        "username": "TaqiSayz"
                    }
                ],
                "CTR": "2",
                "GTR": "st_tw_7146",
                "target_subtype": "profile",
                "target_type": "twitter"
            }
        ]
    })

    # Verify updated list
    print(listObj)

    with open(filename, 'w') as json_file:
        json.dump(listObj, json_file,
                  indent=4,
                  separators=(',', ': '))

    print('Successfully appended to the JSON file')

schedule.every(3).seconds.do(update_json)

while True:
    schedule.run_pending()
    time.sleep(1)