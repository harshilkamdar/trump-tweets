from __future__ import print_function
import numpy as np
import random
import sys
import h5py
import os
import random
import argparse
import configparser as ConfigParser
from keras.models import model_from_json
import tweepy 
import time

model = model_from_json(open('model.txt').read())
model.load_weights('model.h5')

text = open('trump.txt').read().lower()
chars = set(text)
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))

maxlen = 20
step = 3
sentences = []
next_chars = []

for i in range(0, len(text) - maxlen, step):
    sentences.append(text[i: i + maxlen])
    next_chars.append(text[i + maxlen])

X = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        X[i, t, char_indices[char]] = 1
    y[i, char_indices[next_chars[i]]] = 1

def sample(a, temperature=1.0):
    # helper function to sample an index from a probability array
    a = np.log(a) / temperature
    a = np.exp(a) / np.sum(np.exp(a))
    return np.argmax(np.random.multinomial(1, a, 1))

def random_line(afile):
    lines = open(afile).read().lower().splitlines()
    while 1:
        myline = random.choice(lines)
        if(myline[0] != '"'):
            return myline

while 'Trump' != 'President':
	randline = random_line('trump.txt')
	diversity = np.random.uniform(0.25, 0.5, 1)
	generated = ''
	sentence = randline[0:20]
	generated += sentence
	for iteration in range(120):
		x = np.zeros((1, maxlen, len(chars)))
		for t, char in enumerate(sentence):
			x[0, t, char_indices[char]] = 1.
		preds = model.predict(x, verbose=0)[0]
		next_index = sample(preds, diversity)
		next_char = indices_char[next_index]
		generated += next_char
		sentence = sentence[1:] + next_char
	tweet = generated.rsplit(' ', 1)[0]
	config = ConfigParser.ConfigParser()
	config.read("/Users/harshilkamdar/local.cfg")
	sect = "twitter"
	auth = tweepy.OAuthHandler(config.get(sect, "consumer_key"),
	                       config.get(sect, "consumer_secret"))
	auth.set_access_token(config.get(sect, "user_key"),
	                      config.get(sect, "user_secret"))
	api = tweepy.API(auth)
	api.update_status(status=tweet)
	time.sleep(600)	
