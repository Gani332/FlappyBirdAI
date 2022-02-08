import nltk
from nltk.stem.lancaster import LancasterStemmer

stemmer = LancasterStemmer()

import numpy as np
import tflearn
import tensorflow
import random
import json
import pickle

with open("intents.json") as files:
    data = json.load(files)

try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)

except:
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:  # Will loop through Json File
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)  # Stemming gets root of words (doesn't have to be typed word for word)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w not in "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(
        labels))]  # determines if a word exists or if it doesn't uses 1s and 0s depending on frequency can find in video between 5min-9min: https://www.youtube.com/watch?v=ON5pGUJDNow

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)  # Adding a one to show that this word exists
            else:
                bag.append(0)
        output_row = out_empty[:]
        output_row[
            labels.index(docs_y[x])] = 1  # Seeds where tag is in that list and sets that value to 1 in output row

        training.append(bag)
        output.append(
            output_row)  # output and labels are *Hot Encoded* - t is called one-hot because only one bit is “hot” or TRUE at any time. For example, a one-hot encoded FSM with three states would have state encodings of 001, 010, and 100. Each bit of state is stored in a flip-flop, so one-hot encoding requires more flip-flops than binary encoding.

        training = np.array(training)
        output = np.array(output)

        with open("data.pickle", "wb") as f:
            pickle.dump((words, labels, training, output), f)

tensorflow.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training[0])])  # Finding input length of training model
net = tflearn.fully_connected(net, 8)  # 8 neurons in hidden layer
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]),
                              activation="softmax")  # Gives us probability for each neuron in each layer
net = tflearn.regression(net)
model = tflearn.DNN(net)

try:
    model.load("model.tflearn")
except:
    model.fit(training, output, n_epoch=1000, batch_size=8,
              show_metric=True)  # Showing the model the data 1000 times ( n_epoch set to 1000)
    model.save("model.tflearn")


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(words.lower()) for word in s_words]

    for se in s_words:  # Appending to show word exists in sentence
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return np.array(bag)


def chat():
    print("start talking with the bot! (Enter 'quit' to stop)")
    while True:
        inp = input("You: ")
        if inp.lower() == "quit":
            break
        results = model.predict([bag_of_words(inp, words)])[0]
        results_index = np.argmax(results)  # Gives us index of greatest value in our list
        tag = labels[results_index]

        if results[results_index] > 0.7:
            for tg in data["intents"]:
                if tg['tag'] == tag:
                    responses = tg['responses']

            print(random.choice(responses))
        else:
            print("I didn't get that, try again")


chat()
