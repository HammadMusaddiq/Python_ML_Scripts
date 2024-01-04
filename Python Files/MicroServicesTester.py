import time
import requests, json
from pprint import pprint
import re
from multiprocessing import Process

IPADDRESS = "10.100.104.250"

post = ['Amber Heard, in her sob-story-defeat speech said "I`m even more disappointed in what this verdict  means for other women"\
        on behalf of other women, I can confirm we are absolutely DELIGHTED with the verdict 🥂 #TruthWins #JusticeForJohnnyDepp #JohnnyDepp', \
        'don’t think #teamAmberHeard realizes a lot of us who believe #JohnnyDepp are part of the 97%, are WOMEN and have experienced some sort \
        of abuse in our life. We watched the trial, we saw the evidence, we chose who to believe']   

link = "http://10.100.103.114/osint_system/media_files/AI_Video_Analytics/hamza.jpg"


def remove_chars(t):
    t = re.sub(r'\.+', ".", t)
    t = re.sub('[\(\)\[\]\"\*\”\`\“:^-_><]', '', t)
    t = re.sub('/', '', t)
    t = re.sub("\s\s+", " ", t)
    t = re.sub(r'([a-z])\1\1+', r'\1\1', t)
    return t


def get_output(docs):
    words = []
    ents = []

    labels_list = docs[1]

    words_list = docs[0]

    for i in range(0, len(words_list)):
        tokens = words_list[i]
        tags = labels_list[i]

        x = tokens
        y = tags
        y = bio_to_biluo(y)
        # getting the lists for words and their entity labels
        for i in range(0, len(y)):
            entity = ""
            if y[i][0] == 'U':
                entity = str(x[i])
                words.append(entity)
                ents.append(y[i][2:])

            if y[i][0] == 'B' and (y[i][2:] == y[i + 1][2:]):

                entity = str(x[i])

                j = i + 1
                i = i + 1
                while (y[j][0] == 'I'):  # and y[j][2:] == y[j - 1][2:]):
                    entity = entity + " " + str(x[j])

                    j = i + 1
                    if j > (len(y) - 2):
                        break
                    i = i + 1

                if y[i][0] == 'L' and (y[i][2:] == y[i - 1][2:]):
                    entity = entity + " " + str(x[i])

                    words.append(entity)
                    ents.append(y[i][2:])

    return words, ents


def change_char(s, p, r):  # s is the original string, p is the position to change, r is the replacement char
    return s[:p] + r + s[p + 1:]


def bio_to_biluo(y):
    for i in range(0, len(y)):  # get proper IBO tags

        if len(y) == 1:
            y[i] = change_char(y[i], 0, "U")

        if y[i][0] == 'I' and y[i - 1][0] == 'O':
            y[i] = change_char(y[i], 0, "B")

        if y[i][0] == 'I' and y[i - 1][0] == 'I' and (y[i][2:] != y[i - 1][2:]):
            y[i] = change_char(y[i], 0, "B")

        if y[i][0] == 'I' and y[i - 1][0] == 'B' and (y[i][2:] != y[i - 1][2:]):
            y[i] = change_char(y[i], 0, "B")

        if y[i][0] == 'B' and y[i - 1][0] == 'B' and (y[i][2:] == y[i - 1][2:]):
            y[i] = change_char(y[i], 0, "I")

    for i in range(0, len(y)):  # convert to biluo

        if i == 0 or i == len(y) - 1:
            if i == len(y) - 1:
                if y[i][0] == 'B' and (y[i][2:] != y[i - 1][2:]):
                    y[i] = change_char(y[i], 0, "U")
                if y[i][0] == 'B' and (y[i][2:] == y[i - 1][2:]):
                    y[i] = change_char(y[i], 0, "L")
                if y[i][0] == 'I':
                    y[i] = change_char(y[i], 0, "L")

            else:
                if y[i][0] == 'B' and (y[i][2:] != y[i + 1][2:]):
                    y[i] = change_char(y[i], 0, "U")
        else:

            if y[i][0] == 'B' and (y[i][2:] != y[i + 1][2:] and y[i][2:] != y[i - 1][2:]):
                y[i] = change_char(y[i], 0, "U")

            if y[i][0] == 'I' and (y[i][2:] != y[i + 1][2:] and y[i][2:] != y[i - 1][2:]):
                y[i] = change_char(y[i], 0, "U")

            if y[i][0] == 'I' and (y[i + 1][0] == 'O' or y[i + 1][0] == 'B') and (y[i][2:] == y[i - 1][2:]):
                y[i] = change_char(y[i], 0, "L")
    return y


def ner_processing(text):
    list_of_text = []
    
    list_of_t = text.split("\n")
    for t in list_of_t:
        if len(t) <= 1:
            continue

        t = remove_chars(t)
        toks = t.split()
        while len(toks) >= 256:
            temp = toks[:256]
            toks = toks[256:]
            t_str = str(" ".join(temp))
            list_of_text.append(t_str)

        list_of_text.append(" ".join(toks))
    
    return list_of_text


def ner_request(list_of_text):
    words = []
    ents = []

    start = time.time()
    response = requests.post(f"http://{IPADDRESS}:5001/", json={"text": list_of_text})
    end = time.time()
    if response.status_code in [200, 201]:
        print("NER              ==> Checked, Time taken: " + str(round((end - start),2)) + " seconds.")
        docs = response.json()["data"]
        words, ents = get_output(docs)
    else:
        print("NER              ==> Failed")

    print ({'entities': words, 'labels': ents})
    return {'entities': words, 'labels': ents}


def NER(input_text):
    try:
        if input_text is None or input_text == "":
            return {'entities': [], 'labels': []}

        else:
            ner_output = {'entities': [], 'labels': []}
            if type(input_text) == str:
                list_of_text = ner_processing(input_text)
                ner_output = ner_request(list_of_text)

            elif type(input_text) == list:
                list_of_text = []
                for text in input_text:
                    list_of_text.extend(ner_processing(text))  
                ner_output = ner_request(list_of_text) # single string in a list
            
            return ner_output
    
    except Exception as E:
        print(f"ERROR in NER, with Error: {E}")
        return str(E), 500


def Categorize(target_text):
    try:
        start = time.time()
        response = requests.post(f"http://{IPADDRESS}:5012/", json={"text": target_text, "platform": "twitter"})
        end = time.time()

        if response.status_code in [200,201]:
            print("Text Cat         ==> Checked, Time taken: " + str(round((end - start),2)) + " seconds.")
            print (response.json())
            return response.json()

        else:
            print("Text Cat         ==> Failed")
            return {""}


    except Exception as E:
        print(f"ERROR in Text Cat, with Error: {E}")
        return str(E), 500


def emotion_microservices(x):
    try:
        start = time.time()
        response = requests.post(f"http://{IPADDRESS}:5016/", json={"text": str(x)})
        end = time.time()

        if response.status_code in [200,201]:
            print("Emosent          ==> Checked, Time taken: " + str(round((end - start),2)) + " seconds.")
            print (response.json())
            return response.json()

        else:
            print("Emosent          ==> Failed")
            return {""}

    except Exception as E:
        print(f"ERROR in Emosent, with Error: {E}")
        return str(E), 500


def object_detection(link):
    try:
        start = time.time()
        response = requests.post(f"http://{IPADDRESS}:5002/", json={"imageUrl": link})
        end = time.time()

        if response.status_code in [200,201]:
            print("Object Detection ==> Checked, Time taken: " + str(round((end - start),2)) + " seconds.")
            print (response.json())
            return response.json()

        else:
            print("Object Detection ==> Failed")
            return {""}

    except Exception as E:
        print(f"ERROR in Object Detection, with Error: {E}")
        return str(E), 500
    

def weapon_detection(link):
    try:
        start = time.time()
        response = requests.post(f"http://{IPADDRESS}:5017/insert", json={"image_path": link})
        end = time.time()

        if response.status_code in [200,201]:
            print("Weapon Detection ==> Checked, Time taken: " + str(round((end - start),2)) + " seconds.")
            print (response.json())
            return response.json()

        else:
            print("Weapon Detection ==> Failed")
            return {""}

    except Exception as E:
        print(f"ERROR in Weapon Detection, with Error: {E}")
        return str(E), 500
    

def frs(link):
    try:
        start = time.time()
        response = requests.post(f"http://{IPADDRESS}:5003/", json={"imageUrl": link})
        end = time.time()
        if response.status_code in [200,201]:
            print("FRS              ==> Checked, Time taken: " + str(round((end - start),2)) + " seconds.")
            print (response.json())
            return response.json()

        else:
            print("FRS              ==> Failed")
            return {""}

    except Exception as E:
        print(f"ERROR in FRS, with Error: {E}")
        return str(E), 500


if __name__ == '__main__':

    single_string = ' '.join(post) # list of strings in a single string

    for i in range(3):
        p1 = Process(target=NER, args=(post,))
        p2 = Process(target=Categorize, args=(single_string,))
        p3 = Process(target=emotion_microservices, args=(post,))
        p4 = Process(target=object_detection, args=(link,))
        p5 = Process(target=weapon_detection, args=(link,))
        p6 = Process(target=frs, args=(link,))
        p1.start()
        p2.start()
        p3.start()
        p4.start()
        p5.start()
        p6.start()
        p1.join()
        p2.join()
        p3.join()
        p4.join()
        p5.join()
        p6.join()
        print("===============================================")