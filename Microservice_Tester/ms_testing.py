mport time
import requests, json
from pprint import pprint
from pyspark.sql import Row
import re
from multiprocessing import Process

emotionIP = "10.100.103.123"
IPADDRESS = ""
ner_api_url = "10.100.103.123:5001"

ner_api_url = "http://" + str(ner_api_url) + "/"
print(ner_api_url)

ENV = ""
if ENV == "Dev":
    IPADDRESS = "10.100.102.123"
else:
    IPADDRESS = "10.100.103.123"


def remove_chars(t):
    t = re.sub(r'\.+', ".", t)
    t = re.sub('[\(\)\[\]\"\*\"\`\":^-_><]', '', t)
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


def NER(input_text):
    # print("==========================NER Request Started ===========================")
    if input_text is None or input_text == "":

        words = []
        ents = []

        return Row('entities', 'labels')(words, ents)

    else:
        words = []
        ents = []
        list_of_text = []

        if type(input_text) == str:
            text = input_text
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
            starttime = time.time()
            response = requests.post(ner_api_url, json={"text": list_of_text})
            endtime = time.time()

            print("Time taken by NER", endtime - starttime)

            docs = response.json()["data"]
            words, ents = get_output(docs)

        if type(input_text) == list:
            for text in input_text:
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
            starttime = time.time()
            response = requests.post(ner_api_url, json={"text": list_of_text})
            endtime = time.time()

            print("Time taken by NER", endtime - starttime)

            docs = response.json()["data"]

            words, ents = get_output(docs)
        # print("==========================NER Request Ended ===========================\n\n")
        return endtime - starttime


def Categorize(x):
    # print("==========================Categorize Request Started ===========================")
    target_text = x

    start = time.time()
    response = requests.post(f"http://{IPADDRESS}:5012/", json={"text": target_text})
    end = time.time()

    total_time_taken = (end - start)
    print("Time Taken By TaxCat API: ", str(round(total_time_taken, 2)), 'seconds')
    pprint(json.loads(response.text))
    # print("==========================Categorize Request Ended ===========================\n\n")
    return total_time_taken


def emotion_microservices(x):
    # print("==========================Emotion Request Started ===========================")
    start = time.time()
    response = requests.post(f"http://{emotionIP}:5004/", json={"text": [str(x)]})
    end = time.time()

    print("Time Taken by LABSE",end - start)
    # print("==========================Emotion Request Ended ===========================\n\n")
    return end-start

if __name__ == '__main__':
    posts = [
        'Amber Heard, in her sob-story-defeat speech said "I'm even more disappointed in what this verdict  means for '
        'other women" on behalf of other women, I can confirm we are absolutely DELIGHTED with the verdict 🥂 '
        '#TruthWins #JusticeForJohnnyDepp #JohnnyDepp ',
        'don't think #teamAmberHeard realizes a lot of us who believe #JohnnyDepp are part of the 97%, are WOMEN, '
        'and have experienced some sort of abuse in our life. We watched the trial, we saw the evidence, we chose who '
        'to believe']
    text = 'Rapidev office is located in NSTP islamabad.'
    posts = posts * 100
    for post in posts:
        p1 = Process(target=NER, args=(post,))
        p2 = Process(target=Categorize, args=(post,))
        p3 = Process(target=emotion_microservices, args=(post,))
        p1.start()
        p2.start()
        p3.start()
        p1.join()
        p2.join()
        p3.join()
        # emotion_microservices(post)
        # NER(post)