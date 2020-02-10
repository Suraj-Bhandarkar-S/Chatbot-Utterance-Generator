from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer
from rasa_nlu import config

from rasa_nlu.model import Metadata,Interpreter

# Create your views here.
def UG(request):
    return render(request, "CHUG/utterance_generator.html")


import re
import json
from nltk.corpus import wordnet
import nltk


def utterances(utterance):
    getinput = re.search(r"\(([^\(\)]+)\)", utterance)
    if not getinput:
        w = [utterance]
        return w
    getwordlist = getinput.group(0)
    appendinglist = getinput.group(1).split("|")

    w = [
        a
        for w in appendinglist
        for a in utterances((utterance.replace(getwordlist, " "+w+" ", 1)))
    ]
    return w


def value(entities):
    getinput = re.search(r"\(([^\(\)]+)\)", entities)
    if not getinput:
        w = [entities]
        return w
    getwordlist = getinput.group(0)
    appendinglist = getinput.group(1).split("|")
    w = [a for w in appendinglist for a in value((entities.replace(getwordlist, w, 1)))]
    return w


def jsonformatter(intent, utter, entity, values, ent):

    for u in range(len(utter)):
        try:
            if u - 1 >= len(utter):
                u = 0
            if values[u] in utter[u]:
                word = str(values[u])
                print(word)
        except:
            pass
        if entity == "":
            g1 = {"text": str(utter[u]), "intent": intent, "entities": []}
            with open("main/Bank_Data.json") as json_file:
                datas = json.load(json_file)
                temp = datas["rasa_nlu_data"]["common_examples"]
                temp.append(g1)
                write_json(datas)

        else:
            value = re.search(r"\{([^}]+)\}", utter[u]).group(0).strip(" {").strip("} ")
            match = re.search(value, utter[u])
            g1 = {
                "text": str(re.sub("[^A-Za-z0-9]+", " ", utter[u])),
                "intent": intent,
                "entities": [
                    {
                        "start": utter[u].index(value),
                        "end": match.end(),
                        "value": re.search(r"\{([^}]+)\}", utter[u])
                        .group(0)
                        .strip(" {")
                        .strip("} "),
                        "entity": ent,
                    }
                ],
            }
            with open("main/Bank_Data.json") as json_file:
                datas = json.load(json_file)
                temp = datas["rasa_nlu_data"]["common_examples"]
                temp.insert(0, g1)
                write_json(datas)

    return temp


def write_json(data, filename="main/Bank_Data.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def input(request):
    if request.method == "POST":

        intent = request.POST.get('intent')
        string = request.POST.get('TG')
        entities = request.POST.get('entity')
        synonyms = []

        if entities != "":
            entity = re.search(r"\{([^}]+)\}", string).group(0).strip("{").strip("}")
            for syn in wordnet.synsets("entity"):
                for l in syn.lemmas():
                    synonyms.append(l.name())
            ent = entity
            string = string.replace(entity, entities)
            values = value(entities)
            utter = utterances(string)
            data = jsonformatter(intent, utter, entity, values, ent)
            print(json.dumps(data, indent=2))

        else:
            utter = utterances(string)
            data = jsonformatter(intent, utter, "", "", "")
            print(json.dumps(data, indent=2))
    else:
        return render(request, "CHUG/utterance_generator.html")
    
    return render(request, 'CHUG/utterance_generator.html', {'data':data,'utter':utter})


def rasa(request):
    return render(request, "CHUG/rasa.html")
 
def rasa_base(request):
    if request.method == "POST":
        user=request.POST.get('user')
        training_data=load_data('main/Bank_Data.json')
        trainer=Trainer(config.load('main/config_spacy.yml'))
        trainer.train(training_data)
        model_directory= trainer.persist('main/')
        interpreter=Interpreter.load(model_directory)
        print(user)
        output=interpreter.parse(str(user))
    else:
        return render(request, "CHUG/rasa.html")
    
    return render(request, 'CHUG/rasa.html', {'data':output})


