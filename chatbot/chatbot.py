import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import tflearn
import tensorflow
import random
import json
import requests
import pickle


file = open("intents.json") 
data = json.load(file)


# try catch bloc to avoid running all process if model is ready,eliminate it if needed)
try:      
        with open("data.pickle","rb") as f:
            words,labels,training,output = pickle.load(f)

except: 


    docs_x=[]        #list of patterns
    docs_y=[]        #list of patterns tags 
    labels=[]        #list of existing tags 
    words=[]
    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds=nltk.word_tokenize(pattern)   # divide label into list of words (split)
            words.extend(wrds)
            docs_x.append(wrds)               #add pattern
            docs_y.append(intent["tag"])         #add convenient tag
        if intent["tag"] not in labels:
            labels.append(intent["tag"])       #build list of tags 

    words = [stemmer.stem(w.lower())  for w in words if w !="?"] #A processing for removing morphological affixes from words. This process is known as stemming.
    words = sorted( list(set(words)))

    labels = sorted(labels)

    training =[]
    output=[]

    out_empty = [0 for _ in range(len(labels))]   # full list with 0 at the length of labels list


    for x,doc in enumerate(docs_x):  # enumerate(doc_x) is a "list" of tuples containing the element and its index
        bag=[]
        wrds = [stemmer.stem(w) for w in doc]
        for w in words:
            if w in wrds:
                bag.append(1)       
            else:
                bag.append(0)
        # after an iteration , bag is a list of zeros unless 1's at the positions of the referred words
        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1    # list of zeros unless 1 at the position of the referred label

        training.append(bag)
        output.append(output_row)

    training = numpy.array(training)
    output = numpy.array(output)

    with open("data.pickle","wb") as f:
        pickle.dump((words,labels,training,output),f)



tensorflow.reset_default_graph()

net = tflearn.input_data(shape=[None,len(training[0])])    #set shape to length of training data 
net = tflearn.fully_connected(net,10) #build hidden layer with 8 neurons 
net = tflearn.fully_connected(net,10) #another hidden layer
net = tflearn.fully_connected(net,len(output[0]),activation="softmax") #output layer with 6 neurons (number of targets),the neuron with higher prediction is chosen
net = tflearn.regression(net)

# The goal is to find the tag of every input ,in order to generate then the convenient answer

model = tflearn.DNN(net) #DNN :deep neural network 


try:       #load the model if it exists
    model.load("model.tflearn")
except:
    model.fit(training,output, n_epoch=1200,batch_size=8,show_metric=True)  # n_epoch : how much model sees data
    model.save("model.tflearn")


def bag_of_words(s,words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words :
        for i,w in enumerate(words) :
            if se == w:
                bag[i]=1

    return numpy.array(bag)


def answer(inp):
        results = model.predict([bag_of_words(inp,words)])[0]  # list of probabilities of each output neuron 
        index = numpy.argmax(results)      # extract the index of the biggest probability in numpy array 
        if results[index]>0.7:
            tag = labels[index]
            for tg in data["intents"]:
                if tg["tag"] == tag:
                    responses = tg["responses"]
                    break
            return (random.choice(responses))
        else:
            return("I don't really understand , can you try again ?") 
            









