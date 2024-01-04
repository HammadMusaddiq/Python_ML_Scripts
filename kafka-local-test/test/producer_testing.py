from datetime import datetime
import time
import json
from kafka import KafkaProducer
from faker import Faker
import random
import uuid

fake = Faker()


def json_serializer(data):
    return json.dumps(data).encode("utf-8")


def get_partitions(key, all, availaible):
    return 0  # for sending data to only partition 1


producer = KafkaProducer(bootstrap_servers=['10.100.102.110:6667'],
                         value_serializer=json_serializer,
                         # partitioner=get_partitions)
                         )

if __name__ == "__main__":

# https://www.youtube.com/watch?v=0aqiPyTJv8E short video of 3 mins
# https://www.youtube.com/watch?v=ra_TSB2wuLA 24 min video
# http://10.100.102.114/osint_system/media_files/Trimmed_videos/1651041050803764.mp4 downloaded video
# http://10.100.102.114/osint_system/media_files/Trimmed_videos/165063056642382.mp4 10 sec video
# http://10.100.102.114/osint_system/media_files/Trimmed_videos/165095749870404.mp4 1 min video
# http://10.100.102.114/osint_system/media_files/Trimmed_videos/165088767856759.mp4 20 min long video
    
    
    video_urls = ['http://10.100.102.114/osint_system/media_files/Trimmed_videos/165088767856759.mp4']

    while True:
        
        id = uuid.uuid1()
        url_count = random.randrange(0,3)

        # inserting data to topic then read, online video_url (videos-to-be-downloaded)
        # test = {
        #     "kafka_id": id.hex,
        #     "video_url": random.choice(video_urls),
        #     "start_video": '00:01:00',
        #     "end_video": '00:02:00' 
                   
        # }


        # inserting data to topic then read, local ftp_video_url (cryptix-videos) 
        # test = {
        #     "kafka_id": id.hex,
        #     "video_url": random.choice(video_urls),
        #     "start_video": '00:01:00',
        #     "end_video": '00:02:00' 
                   
        # }
        

        # reading data from topic, online video_url (trimmed-videos)
        # test = {
        #     "kafka_id": id.hex,
        #     "trimmed_url": random.choice(video_urls),
        #     "topic": "trimmed-videos"
        # }


        # # reading data from topic, Local ftp_video_url (trimmed-videos-local)
        # test = {
        #     "kafka_id": id.hex,
        #     "trimmed_url": random.choice(video_urls),
        #     "topic": "trimmed-videos"
        # }


        # reading data from topic, Local ftp_video_url (mp3-to-be-transcribed)
        # test = {
        #     "kafka_id": id.hex,
        #     "audio_url": 'https://cdn.pagalworld.us/songs/bollywood/Dhadkan%202000%20-%20Na%20Na%20Karte%20Pyar.mp3',
        #     "data_type": "audio_transcription"
        # }

        # test = {
        #     "transcription": "The game is based on previous mods that were created by Brendan 'PlayerUnknown' Greene for other games, inspired by the 2000 Japanese film Battle Royale, and expanded into a standalone game under Greene's creative direction"
        # }
        

        test = {
                "text_c": "Army is taking part in pakistani politics, why?",
                "target_information": 
                {
                "target_type": "face",
                },
                "kafka_id":id.hex,
                "topic": "categorization_input_test",
                "data_type": "categorization_input_test"
        }


        # preprocessing-completed Data
        # test = {
        #     "author": {
        #         "image": "",
        #         "is_verified": 0,
        #         "name": "",
        #         "url_c": "",
        #         "username": ""
        #     },
        #     "comments": [
        #         {
        #         "commenter": {
        #             "id": "",
        #             "image": "",
        #             "name": "Catie King",
        #             "url": "",
        #             "username": "C_Pj_K"
        #         },
        #         "media": [],
        #         "reply_to": "Replying to \n@Adele",
        #         "text": "What the actual fuck. So we just gna forget about Vegas then?",
        #         "timestamp": 1643725052,
        #         "url": "https://twitter.com/C_Pj_K/status/1488592369289211911"
        #         },
        #         {
        #         "commenter": {
        #             "id": "",
        #             "image": "",
        #             "name": "Dave",
        #             "url": "",
        #             "username": "DaveMFC1984"
        #         },
        #         "media": [],
        #         "reply_to": "Replying to \n@Adele",
        #         "text": "Least no one is going to lose any money on you dropping out after thousands of tickets purchased.",
        #         "timestamp": 1643725152,
        #         "url": "https://twitter.com/DaveMFC1984/status/1488592791978618890"
        #         },
        #         {
        #         "commenter": {
        #             "id": "",
        #             "image": "",
        #             "name": "Dimpho Nomvalo",
        #             "url": "",
        #             "username": "__Dimpho__Nia__"
        #         },
        #         "media": [],
        #         "reply_to": "Replying to \n@Adele",
        #         "text": "She just crushed every rumour y’all made up",
        #         "timestamp": 1643723427,
        #         "url": "https://twitter.com/__Dimpho__Nia__/status/1488585554170376193"
        #         },
        #         {
        #         "commenter": {
        #             "id": "",
        #             "image": "",
        #             "name": "#Adele30",
        #             "url": "",
        #             "username": "angie53070613"
        #         },
        #         "media": [],
        #         "reply_to": "",
        #         "text": "LMAO",
        #         "timestamp": 1643723885,
        #         "url": "https://twitter.com/angie53070613/status/1488587474821648388"
        #         },
        #         {
        #         "commenter": {
        #             "id": "",
        #             "image": "",
        #             "name": "B",
        #             "url": "",
        #             "username": "Brian_Chinnici"
        #         },
        #         "media": [],
        #         "reply_to": "Replying to \n@Adele",
        #         "text": "So you\u0027re holding a card in your had and laughing at everyone who bought tickets to your Vegas shows you cancelled because you\u0027re a diva and had crazy demands.  Hello...",
        #         "timestamp": 1643723778,
        #         "url": "https://twitter.com/Brian_Chinnici/status/1488587026396073984"
        #         },
        #         {
        #         "commenter": {
        #             "id": "",
        #             "image": "",
        #             "name": "Jarvis Aeon",
        #             "url": "",
        #             "username": "AeonJarvis"
        #         },
        #         "media": [],
        #         "reply_to": "",
        #         "text": "Even if Adele had crazy demands, I’m sure they would’ve done anything they could to meet them. This is Adele! One of the most famous entertainers on the planet. I believe her story 100%.",
        #         "timestamp": 1643736520,
        #         "url": "https://twitter.com/AeonJarvis/status/1488640471563968518"
        #         },
        #         {
        #         "commenter": {
        #             "id": "",
        #             "image": "",
        #             "name": "shawn Campbell",
        #             "url": "",
        #             "username": "uchihashawn"
        #         },
        #         "media": [],
        #         "reply_to": "Replying to \n@Adele",
        #         "text": " coming soon. Music industry about to flipped on it\u0027s head.",
        #         "timestamp": 1643904832,
        #         "url": "https://twitter.com/uchihashawn/status/1489346423728529409"
        #         },
        #         {
        #         "commenter": {
        #             "id": "",
        #             "image": "",
        #             "name": "ScottyRichard",
        #             "url": "",
        #             "username": "ScottRi07099692"
        #         },
        #         "media": [],
        #         "reply_to": "Replying to \n@Adele",
        #         "text": "Shocking.\nThose fans you let down in Vegas would have been more than happy for you to sit yourself and just sing as you did at the Brits.\nBut no...them spending thousands doesn\u0027t matter does it.",
        #         "timestamp": 1644337824,
        #         "url": "https://twitter.com/ScottRi07099692/status/1491162523261083650"
        #         },
        #         {
        #         "commenter": {
        #             "id": "",
        #             "image": "",
        #             "name": "Jeff Lynde",
        #             "url": "",
        #             "username": "DeeOhblah"
        #         },
        #         "media": [],
        #         "reply_to": "Replying to \n@Adele",
        #         "text": "She still owes these people a rescheduled show from 2017.\nJune 28-29 \u0026 July 1-2, 2017 Wembley Stadium, London, ENG (July 1st \u0026 2nd were cancelled due to vocal injuries)",
        #         "timestamp": 1643757333,
        #         "url": "https://twitter.com/DeeOhblah/status/1488727768133079040"
        #         },
        #         {
        #         "commenter": {
        #             "id": "",
        #             "image": "",
        #             "name": "Rachel IStandWithUkraine",
        #             "url": "",
        #             "username": "rachel_clewlow"
        #         },
        #         "media": [],
        #         "reply_to": "Replying to \n@Adele",
        #         "text": "Oooooooh dear, this probably isn\u0027t the best tweet, obviously you\u0027ll be refunding your fans for your canx show, but will you be sorting out their flights and hotel costs as well, plus people having to take time off work as well. Think there will be a few discrumpled fans.",
        #         "timestamp": 1643772737,
        #         "url": "https://twitter.com/rachel_clewlow/status/1488792374386073605"
        #         },
        #         {
        #         "commenter": {
        #             "id": "",
        #             "image": "",
        #             "name": "POWR FFearFFul",
        #             "url": "",
        #             "username": "FFearFFul"
        #         },
        #         "media": [],
        #         "reply_to": "Replying to \n@Adele",
        #         "text": "اول",
        #         "timestamp": 1643723362,
        #         "url": "https://twitter.com/FFearFFul/status/1488585284124086277"
        #         },
        #         {
        #         "commenter": {
        #             "id": "",
        #             "image": "",
        #             "name": "fan Towfiq .",
        #             "url": "",
        #             "username": "ilove_Towfiq"
        #         },
        #         "media": [],
        #         "reply_to": "",
        #         "text": "ههههههههههههههههههههههههههههههههههههههههههههههههههههههههههههههههههههههههههههههههه",
        #         "timestamp": 1644135198,
        #         "url": "https://twitter.com/ilove_Towfiq/status/1490312648830947328"
        #         }
        #     ],
        #     "data_type": "twitter_posts",
        #     "device_used": "Twitter for iPhone",
        #     "id": "1488585221066928139",
        #     "impressions": {
        #         "no_of_comments_c": "3,119",
        #         "no_of_quote_tweets": "2,076",
        #         "no_of_reactions_c": "121K",
        #         "no_of_shares": "7,440"
        #     },
        #     "kafka_id": "d811ab4d-227f-442a-9f7f-60559fd8b19d",
        #     "media_c": [
        #         "http://10.100.102.114/osint_system/media_files/MDS_Downloads/MDS_Image/Img30052022-160623.jpeg"
        #     ],
        #     "reactions": {
        #         "like": [
        #         {
        #             "image": "https://pbs.twimg.com/profile_images/1531215803084857344/PT6-elDl_normal.png",
        #             "name": "Promise Isaac",
        #             "url": "https://twitter.com/Promise45037201",
        #             "username": "Promise45037201"
        #         },
        #         {
        #             "image": "https://pbs.twimg.com/profile_images/1484045302839791616/I2DYShf-_normal.jpg",
        #             "name": "Nandini Gupta",
        #             "url": "https://twitter.com/VScintillant",
        #             "username": "VScintillant"
        #         },
        #         {
        #             "image": "https://pbs.twimg.com/profile_images/1508847969797394453/owZdKyVO_normal.jpg",
        #             "name": "BokonBie",
        #             "url": "https://twitter.com/BokonBie",
        #             "username": "BokonBie"
        #         },
        #         {
        #             "image": "https://pbs.twimg.com/profile_images/1531144685242265600/a_JDacbw_normal.jpg",
        #             "name": "Im__eall_v",
        #             "url": "https://twitter.com/Im__eall_v",
        #             "username": "Im__eall_v"
        #         },
        #         {
        #             "image": "https://pbs.twimg.com/profile_images/1529196517617041408/UZ2Fe7el_normal.jpg",
        #             "name": "Matayo_1992",
        #             "url": "https://twitter.com/matayo_1992",
        #             "username": "matayo_1992"
        #         },
        #         {
        #             "image": "https://pbs.twimg.com/profile_images/1516398369996144641/-88PKqO6_normal.jpg",
        #             "name": "",
        #             "url": "https://twitter.com/olympeschgetter",
        #             "username": "olympeschgetter"
        #         },
        #         {
        #             "image": "https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png",
        #             "name": "LinfoCD8",
        #             "url": "https://twitter.com/Cd8Linfo",
        #             "username": "Cd8Linfo"
        #         },
        #         {
        #             "image": "https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png",
        #             "name": "ariana",
        #             "url": "https://twitter.com/ariana22513605",
        #             "username": "ariana22513605"
        #         },
        #         {
        #             "image": "https://pbs.twimg.com/profile_images/1319296417433870336/_O-9bSVs_normal.jpg",
        #             "name": "highwasted",
        #             "url": "https://twitter.com/highwasted1",
        #             "username": "highwasted1"
        #         },
        #         {
        #             "image": "https://pbs.twimg.com/profile_images/1529260889425207296/OxuL8TAi_normal.jpg",
        #             "name": "4o4a",
        #             "url": "https://twitter.com/mohameed_3li_",
        #             "username": "mohameed_3li_"
        #         },
        #         {
        #             "image": "https://pbs.twimg.com/profile_images/1485850797514633217/IbMf2_Xi_normal.png",
        #             "name": "Juan Pérez",
        #             "url": "https://twitter.com/jp633622",
        #             "username": "jp633622"
        #         },
        #         {
        #             "image": "https://pbs.twimg.com/profile_images/1497258915209306115/QM17ZmbK_normal.png",
        #             "name": "Sia Kangbia",
        #             "url": "https://twitter.com/Tigath43",
        #             "username": "Tigath43"
        #         },
        #         {
        #             "image": "https://pbs.twimg.com/profile_images/1530962733939695621/giT8LZ8P_normal.jpg",
        #             "name": "Amir",
        #             "url": "https://twitter.com/Amir34835517",
        #             "username": "Amir34835517"
        #         },
        #         {
        #             "image": "https://pbs.twimg.com/profile_images/1524483255377874944/zLPNj34l_normal.jpg",
        #             "name": "Nia ³⁰",
        #             "url": "https://twitter.com/obsessedwithalb",
        #             "username": "obsessedwithalb"
        #         },
        #         {
        #             "image": "https://pbs.twimg.com/profile_images/1530921142898262018/8aCsb4kk_normal.jpg",
        #             "name": "Miss Fischer",
        #             "url": "https://twitter.com/MissFischer1980",
        #             "username": "MissFischer1980"
        #         },
        #         {
        #             "image": "https://pbs.twimg.com/profile_images/1507010016829906947/gTAFJJ8w_normal.jpg",
        #             "name": "Jisoonie",
        #             "url": "https://twitter.com/BlinkArmylvr",
        #             "username": "BlinkArmylvr"
        #         },
        #         {
        #             "image": "https://pbs.twimg.com/profile_images/1530329279472361472/Eb7ciADR_normal.jpg",
        #             "name": "Ldrick",
        #             "url": "https://twitter.com/lrik29",
        #             "username": "lrik29"
        #         }
        #         ]
        #     },
        #     "retweet": False,
        #     "tag_links": [],
        #     "tags": [],
        #     "target_information": {
        #         "CTR": "adele",
        #         "GTR": "adele",
        #         "target_subtype": "profile",
        #         "target_type": "twitter",
        #         "username": "Adele"
        #     },
        #     "text_c": "Hiya, so I’m really happy to say that I am performing at the Brits next week!! Anddddd I’ll also be popping in to see Graham for a chat on the couch while I’m in town too! I’m looking forward to it! Oh, and Rich sends his love ",
        #     "timestamp_c": 1643741340,
        #     "topic": "preprocessing_completed",
        #     "url_c": "https://twitter.com/Adele/status/1488585221066928139",
        #     "video": [],
        #     "mentions": [],
        #     "hashtags": []
        #}


        # registered_user = get_registered_user()
        # print(registered_user)

        producer.send("categorization_input_test", test)

        print(test)
        time.sleep(30) # data after every 1 minute
