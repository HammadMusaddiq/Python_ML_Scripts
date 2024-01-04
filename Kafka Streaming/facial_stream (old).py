
#from os import truncate
#from numpy import true_divide
import datetime
from io import BytesIO
from os import truncate
from PIL import Image
import cv2
import numpy as np
import requests
import torch
from torchvision import models
import pyspark.sql.functions as F
import re
import numpy as np
from OwlsenseStream import OwlsenseStream

def callback(df):
    df1 = df.select('content.posts','target_information.CTR', 'target_information.GTR', 'target_information.target_subtype','target_information.target_type')

    df1 = df1.select('CTR','GTR','target_type','target_subtype','posts.media_c.*')

    #write dataset to JSON file
    df1.to_json('csvdf.json')
    #df1.to_json(orient='index')

    # labels = "/home/rapidev/Downloads/Hammad/Shams Image Classification/ilsvrc2012_wordnet_lemmas.txt"
    # labels = dict(enumerate(open(labels)))
    # #print(labels)

    # def read_from_url(url):
    #     response = requests.get(url)
    #     img = Image.open(BytesIO(response.content))
    #     arr = np.uint8(img)
    #     return arr

    # def preprocess_image(image):
    #     # swap the color channels from BGR to RGB, resize it, and scale the pixel values to [0, 1] range
    #     orig = image.copy()
    #     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #     image = cv2.resize(image, (224, 224))
    #     image = image.astype("float32") / 255.0
    #     # subtract ImageNet mean, divide by ImageNet standard deviation, set "channels first" ordering, and add a batch dimension
    #     image -= [0.485, 0.456, 0.406]
    #     image /= [0.229, 0.224, 0.225]
    #     image = np.transpose(image, (2, 0, 1))
    #     image = np.expand_dims(image, 0)
    #     # return the preprocessed image
    #     return image

    # def preprocess_image_2(image):
    #     return image

    # new = df1.select("media_c").rdd.flatMap(list).collect()

    # for i in range(df1.count()):
    #     image_links=[]

    #     for url in re.findall('(http://\S+)', str(new[i]) ): 
    #         url = url.split("'", 1)
    #         url = url[0]
    #         url = url.split('"',1)
    #         image_links.append(url[0])
        
    #     #print(image_links)
    #     ctr = df1.select('CTR').collect()[i]['CTR']
    #     gtr = df1.select('GTR').collect()[i]['GTR']
    #     target_type = df1.select('target_type').collect()[i]['target_type']
    #     target_subtype = df1.select('target_subtype').collect()[i]['target_subtype']    
        
    #     print('stage image link')
    #     if image_links != [] or None:
    #         print("\n\n ARRAY OF IMAGES :", image_links)
    #         for image in image_links:
    #             current_image = image
    #             print("CURRENT IMAGE :", current_image)
    #             try:    
    #                 image = read_from_url(image)
    #                 if image.size!=2:
    #                     try:
    #                         image = preprocess_image(image)
    #                     except:
    #                         image = preprocess_image_2(image)

    #                     c = 0
    #                     ll = [] #labels list
    #                     DEVICE = "cpu"
    #                     model = models.resnet50(pretrained=True)
    #                     model.eval()
    #                     image = torch.from_numpy(image)
    #                     image = image.to(DEVICE)
    #                     imagenetLabels = labels
    #                     logits = model(image) 
    #                     probabilities = torch.nn.Softmax(dim=-1)(logits)
    #                     sortedProb = torch.argsort(probabilities, dim=-1, descending=True)
    #                     (label, prob) = (imagenetLabels[probabilities.argmax().item()],
    #                                         probabilities.max().item())
    #                     prob *=100
    #                     print(current_image,":",label,"Probability :", prob)

    #                     #df = df.withColumn("post_id", F.lit(postid))
    #                     df1 = df1.withColumn("CTR", F.lit(ctr))
    #                     df1 = df1.withColumn("GTR", F.lit(gtr))
    #                     df1 = df1.withColumn("target_type", F.lit(target_type))
    #                     df1 = df1.withColumn("target_subtype", F.lit(target_subtype))
    #                     df1 = df1.withColumn("images", F.lit(current_image))
    #                     df1 = df1.withColumn("image_classified", F.lit(label))
    #                     df1 = df1.withColumn("probability", F.lit(prob))
    #                     df1 = df1.withColumn("image_analytics_type", F.lit("image_classification"))
    #                     df1 = df1.withColumn("created_on", F.lit(datetime.datetime.now()))
    #                     #print(df.printSchema())
    #                     #print(df1.show())
    #                     print("Saving Data to ES")
    #                     #print(save_to_elastic("image_classification",df))
    #                     print("Data Saved to ES")
    #                 else:
    #                     print("\n\nEMPTY IMAGE :", image)
    #             except:
    #                 print("Image url is expired :",current_image)
    #     else:
    #         print("image does not exist")
    #         #sys.exit()
    #     print("\t*** END ***")
    print(df1.show(truncate=False))
    return df1

stream = OwlsenseStream(read_topic='clean_tweets',write_topic='DDDD',feature_name="TEST")
stream.start(callback=callback)

#spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.7,org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0 --conf spark.sql.caseSensitive=True --py-files /home/rapidev/Downloads/Hammad/Git_Clone/Development/bds/kafka_streaming/OwlsenseStream.py /home/rapidev/Downloads/Hammad/Git_Clone/Development/bds/kafka_streaming/pipeline/facial_stream.py