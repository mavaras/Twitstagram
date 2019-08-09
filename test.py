#!/usr/bin/env python
# encoding: utf-8

import tweepy #https://github.com/tweepy/tweepy
import csv
import os
import sys
import time
import threading
import tempfile
import requests
from flask import Flask, render_template, request, url_for, send_file, after_this_request
app = Flask(__name__)



class Tweet:
	def __init__(self, tid, url, image_url, user_name):
		self.tid = tid
		self.image_url = image_url
		self.url = url
		self.user_name = user_name

@app.route("/", methods = ["GET", "POST"])
def g_index():
	tweets = []
	query_word = ""
	if "query_word" in request.form:
		tweets = get_all_tweets(request.form["query_word"])
		query_word = request.form["query_word"]
		
	return render_template("index.html", tweets=tweets, query_word=query_word)

@app.route("/download_photo/<tid>", methods = ["GET", "POST"])
def download_photo(tid):
	url = api.get_status(tid).entities["media"][0]["media_url"]
	temp = tempfile.NamedTemporaryFile()
	
	try:
		myfile = requests.get(url)
		temp.write(myfile.content)
		
		@after_this_request
		def cleanup(response):
			time.sleep(.2)
			temp.close()
			return response
	
		return send_file(temp.name, as_attachment=True, attachment_filename=str(tid)+"_img."+url.split(".")[-1])

	except Exception as e:
		print(e)
			
def get_all_tweets(query_word, lim=20, langs=["es", "en"]):
	n_images = 0
	tweets = []
	for c, tweet in enumerate(tweepy.Cursor(api.search,
										    q=query_word,
										    result_type="recent",
										    include_entities=True).items()):

		if n_images == lim:		
			print("\n"+str(c)+str(" tweets viewed"))
			break
		
		try:
			imgs = [t.image_url for t in tweets]
			if not tweet.entities["media"][0]["media_url"] in imgs and tweet.lang in langs:
				n_images += 1
				url = "https://twitter.com/"+str(tweet.user.screen_name)+str("/status/"+str(tweet.id))
				tweets.append(Tweet(tweet.id, url,
									str(tweet.entities["media"][0]["media_url"]),
									str(tweet.user.screen_name)))
		except Exception as e:
			pass

	return list(dict.fromkeys(tweets))

if __name__ == "__main__":
	# Twitter API credentials
	consumer_key = "fcu9PcNrN1db0V8KKwzn9u2iD"
	consumer_secret = "XDI4RLlwxFLbJKvxDz9VYrpghKHQpIL20tocOpMPZGjsCEZrwu"
	access_key = "299082686-3BhubbawZ6qtgh2pTitfUMoE1eg8QuQIaaBIZmfL"
	access_secret = "TxjDQYVyK0NWmOFYCVsf1LWd6uW5YxKAuPZGdoodSVazJ"

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)

	# get_all_tweets("avila")
	app.run()

