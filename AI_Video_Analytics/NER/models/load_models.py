
from deeppavlov import configs, build_model

def load_model():
    ner_model = build_model(configs.ner.ner_ontonotes_bert_torch, download=True)
    return ner_model