"""
tweetmeter.py
~~~~~~~~~~~~~

Weekend project testing the possibility of metering tweets
"""

import twitter_apps
import json 
import requests # don't really need this yet
from application_only_auth import Client

def usage():
  pass

def main():
  # init auth and send a simple GET
  client = Client(twitter_apps.API_KEY, twitter_apps.API_SECRET)
  tweet = client.request('https://api.twitter.com/1.1/statuses/show.json?id=465347894480891906')

  print json.dumps(tweet, sort_keys=True, indent=4, separators=(',', ':'))

if __name__ == "__main__":
  main()
