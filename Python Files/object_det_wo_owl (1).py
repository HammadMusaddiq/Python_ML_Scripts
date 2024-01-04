import random
import json
import requests
from pyspark.sql import SparkSession
import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
import datetime
import io
from skimage import io as io_skimage
from elasticsearch import Elasticsearch
import pyspark.sql.functions as F
import configparser
from ftplib import FTP
import matplotlib as mpl


'''
For access path, on cluster user this ("hdfs:///user/config/config.ini") 
on System user this ("hdfs://192.168.18.182/user/config/config.ini")
'''

# configuration for FTP
node_ip_ftp = None
node_port_ftp = None
auth_user_ftp = None
auth_pass_ftp = None

# configuration for OBJD_FLASK
node_ip_objd = None
node_port_objd = None
esip = None
esport = None


colors = ['antiquewhite', 'aqua', 'aquamarine', 'bisque', 'black', 'blanchedalmond', 'blue', 'blueviolet', 'brown',
          'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan',
          'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta',
          'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue',
          'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray',
          'dimgrey', 'dodgerblue', 'firebrick', 'forestgreen', 'fuchsia', 'gainsboro', 'gold', 'goldenrod', 'gray',
          'green', 'greenyellow', 'grey', 'hotpink', 'indianred', 'indigo', 'khaki', 'lawngreen', 'lemonchiffon',
          'lightblue', 'lightcoral', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon',
          'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lime', 'limegreen',
          'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen',
          'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mistyrose',
          'moccasin', 'navajowhite', 'navy', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod',
          'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum',
          'powderblue', 'purple', 'rebeccapurple', 'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon',
          'sandybrown', 'seagreen', 'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'springgreen',
          'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'yellow', 'yellowgreen']


# Method of calling model configuation from DetectronApp using Flask App
def callConfig():
    headers = {
        "Content-Type": "application/json"
    }
    cfg = requests.get(f"http://{node_ip_objd}:{node_port_objd}/get_config", headers=headers).json()
    return cfg['config']


# FTP Server Connection
ftp = None


def connect():
    global ftp
    ftp = FTP()
    try:
        ftp.connect(node_ip_ftp, int(node_port_ftp))
        return True
    except Exception as e:
        print(e)
        return False


def login():
    global ftp
    try:
        ftp.login(auth_user_ftp, auth_pass_ftp)
        return True
    except Exception as e:
        print(e)
        return False


def directory_exists(dir):
    global ftp
    filelist = []
    ftp.retrlines('LIST', filelist.append)
    # print(filelist)
    for f in filelist:
        if f.split()[-1] == dir and f.upper().startswith('D'):
            return True
    return False


def chdir(dir):
    global ftp
    if directory_exists(dir) is False:
        ftp.mkd(dir)
    ftp.cwd(dir)


# Image to FTP
def ftp_connection(var_date, img1):
    try:
        connect()
        try:
            login()
            chdir("Object_Detection")  # Change Directory

            try:
                temp = io.BytesIO()  # This is a file object
                img1.savefig(temp, format="jpeg", bbox_inches='tight', pad_inches=0)  # Save the content to temp
                temp.seek(0)  # Return the BytesIO's file pointer to the beginning of the file

                # Store image to FTP Server
                ftp.storbinary("STOR " + var_date + ".jpeg", temp)
                ftp.quit()

                temp.close()

                IMG = BASE_URL + var_date + ".jpeg"
                return str(IMG)

            except Exception as E:
                print(E)

        except Exception as E:
            print(E)

    except Exception as E:
        print(E)


# FTP Image URL
def ftp_image_url(img1):
    # Image Name Based on Current Time.
    c_time = datetime.datetime.now().today()
    # date_time = c_time.strftime("%d%m%Y-%H%M%S")
    var_date = "Img" + str(datetime.datetime.now().timestamp()).replace(".", "")
    image = ftp_connection(var_date, img1)
    return image


def plot_Image_Boundings(objd_data, img):
    # converting str list to flost list
    objd_data_predicted_axis = []

    for axis in objd_data['predicted_axis']:
        objd_data_predicted_axis.append([float(val) for val in axis])

    if objd_data_predicted_axis:  # If object(s) found in the image

        fig = plt.figure(figsize=(14, 12), facecolor='Black')
        ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], alpha=1.0)
        ax.set_frame_on(False)
        ax.set_xticks([])
        ax.set_yticks([])

        box_axis = []
        box_text = []
        box_color = []
        for _box, _score, _class in zip(objd_data_predicted_axis, objd_data['probability_score'],
                                        objd_data['object_classified']):
            x1, y1, x2, y2 = tuple(_box)  # xmin, ymin, xmax, ymax (x is Top, y is Left)
            # print(x1,y1,x2,y2)
            w, h = x2 - x1, y2 - y1  # width (w) = xmax - xmin ; height (h) = ymax - ymin (w is Right, h is Bottom)

            random_color = colors[random.randrange(0, len(colors) - 1)]
            box_color.extend([random_color])
            box_axis.append([mpl.patches.Rectangle((x1, y1), w, h, fill=False, color=random_color, lw=3)])
            box_text.append([x1 + 2, (y1 + 2), str(_class + ' (' + _score + '%)')])

        for axis, b_text, b_color in zip(box_axis, box_text, box_color):
            for rectangle in axis:
                ax.add_patch(rectangle)

            text_x, text_y, text_s = b_text
            t = ax.text(text_x, text_y, text_s, verticalalignment='top', color="white", fontsize=8, weight='bold')
            t.set_bbox(dict(facecolor=b_color, alpha=0.4, edgecolor='black'))
            t.set_path_effects([PathEffects.withStroke(linewidth=1, foreground="black")])

        ax.get_xaxis().set_visible(False)
        ax.imshow(img)

        image = fig
        plt.close(fig)

        ftp_url = ftp_image_url(image)  # fig has image object
        return ftp_url

    else:  # If no object found in the image, img is numpy array of actual image
        return img



def flatten(list_of_lists):
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flatten(list_of_lists[0]) + flatten(list_of_lists[1:])
    return list_of_lists[:1] + flatten(list_of_lists[1:])


def get_entities(list_of_urls):
    results = {
        "urls": [],
        "predictions": [],
        "confidences": []
    }

    # print(list_of_urls)

    # we are getting single list from elastic serach Data Frame. As we are gettign exploded data from ES
    if not isinstance(list_of_urls, list) or list_of_urls == [] or list_of_urls == None or list_of_urls == [
        'default']:  # if media_c is empty / no-url (Checks for all platforms)
        results["urls"].append("")
        results["predictions"].append([])
        results["confidences"].append([])
        return results
    else:
        list_of_urls = flatten(list_of_urls)  # if media_c is not emtpy
        for image_url in list_of_urls:  # for all platforms including reddit
            if image_url != [] and image_url != None and image_url != 'default':
                try:
                    response = requests.post(f"http://{node_ip_objd}:{node_port_objd}/", json={"imageUrl": image_url})
                    objd = response.json()["data"]
                except Exception as e :
                    return results
                try:
                    objd_data = objd[0]

                    # Read image from URL
                    img = io_skimage.imread(image_url)
                    try:
                        image_output = plot_Image_Boundings(objd_data, img)

                        if isinstance(image_output,
                                      str):  # if object plotted on the image then the return value will be the url of ftp in string
                            results["urls"].append(image_output)
                        else:  # if no object found in the image then image url will be same of input image
                            results["urls"].append(image_url)
                        results["predictions"].append(objd_data['object_classified'])
                        results["confidences"].append(objd_data['probability_score'])
                        # print(results)

                    except Exception as E:
                        print(E)
                except Exception as E:
                    print(E)
                    # print("Image URL is Expired: " + image_url)
                    results["urls"].append("")
                    results["predictions"].append([])
                    results["confidences"].append([])

            else:
                results["urls"].append("")
                results["predictions"].append([])
                results["confidences"].append([])
        '''
        code little updated from here. test by my self (not pushed yet). (if we get multiple urls in a single link and 
        we get empty brackets or None or 'default' it code will not get error) previous code is working as we can be 
        getting multiple urls in a list. and this list would not have empty brackets or None or Default.
        '''
        return results


def callback(df):
    df = df.decode('utf-8')
    es = Elasticsearch(f"http://{esip}:{esport}")
    df = json.loads(df)

    if 'media_c' not in df.keys():
        print("=======================================medic_c not found in the data~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(df.get('kafka_id'))
        return json.dumps(df)

    df['object_detection'] = get_entities(df['media_c'])
    o = df
    data = o['object_detection']
    q = {"script": {"source": "ctx._source.object_detection = params.data", "lang": "painless",
                    'params': {"data": data}},
         "query": {"match": {"kafka_id": o['kafka_id']}}}
    try:
        es.update_by_query(body=q, index=o['data_type'])
        es.indices.refresh(index=o['data_type'])
    except Exception as e:
        print("====================CONFLICT WHILE UPDATING THE RECORD===================")
    return json.dumps(df)


if __name__ == '__main__':

    ip = ""
    conf_path = "hdfs://{}/user/config/config.ini".format(ip)  # Config Path
    checkpoint_location = "/home/ubuntu/Desktop/checkp/object_detection_chk"
    print("Configuration File Path: ", conf_path)

    spark = SparkSession \
        .builder \
        .appName("SSKafka") \
        .getOrCreate()
    # ============================= Reading Config =============================
    credstr = spark.sparkContext.textFile(conf_path).collect()
    buf = io.StringIO("\n".join(credstr))

    parser = configparser.ConfigParser()
    parser.read_file(buf)
    node_ip_ftp = str(parser.get('FTP', 'host')).strip()
    node_port_ftp = str(parser.get('FTP', 'port')).strip()
    auth_user_ftp = str(parser.get('FTP', 'username')).strip()
    auth_pass_ftp = str(parser.get('FTP', 'password')).strip()

    node_ip_objd = str(parser.get('OBJD_FLASK', 'ip')).strip()
    node_port_objd = str(parser.get('OBJD_FLASK', 'port')).strip()
    esip = str(parser.get('BDS_ES_PROD', 'ip'))
    esport = str(parser.get('BDS_ES_PROD', 'port'))

    KAFKA_CONSUMER_IP = str(parser.get('KAFKA_BROKERS', 'brokers'))
    # ============================= END =============================

    print(f"es -> {esip}:{esport}")
    print(f"OBJD -> {node_ip_objd}:{node_port_objd}")
    print(f"FTP -> {node_ip_ftp}:{node_port_ftp}")
        
    # BASE_URL = "http://" + node_ip_ftp + "/osint_system/media_files/Object_Detection/" ## Staging /Dev
    BASE_URL = "http://" + node_ip_ftp + "/microcrawler/Object_Detection/" ## Bahrain/NRTC

    topic_name = 'preprocessing_completed'
    write_topic = "object_detection_processed"

    dfraw = spark.readStream.format('kafka') \
        .option('kafka.bootstrap.servers', KAFKA_CONSUMER_IP) \
        .option('subscribe', topic_name) \
        .load()

    calludf = F.udf(lambda x: callback(x))

    df = dfraw.withColumn('value', calludf(dfraw['value'])) \
        .select('value')

    ds = df.selectExpr("CAST(value AS STRING)") \
        .writeStream \
        .format('console') \
        .option('truncate', False) \
        .option('numRows', 100000) \
        .start()

    dsf = df.selectExpr("CAST (value AS STRING)") \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_CONSUMER_IP) \
        .option("topic", write_topic) \
        .option("checkpointLocation", checkpoint_location) \
        .start()
    # ds.awaitTermination()
    # dsf.awaitTermination()
    spark.streams.awaitAnyTermination()
