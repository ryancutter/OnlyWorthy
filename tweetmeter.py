"""
tweetmeter.py
~~~~~~~~~~~~~

Weekend project testing the possibility of metering tweets
"""

from csv import reader
from datetime import datetime, timedelta

import twitter_apps
from application_only_auth import Client

def usage():
  pass

def getConfig():
  """ read config file and return list of username/# of tweets tuples. """
  with open('config.csv', 'rb') as configfile:
    return [row for row in reader(configfile)]

def evaluate_tweets(tweets, stop_time, start_time):
  """ collect and score all tweets in desired time window. return ranked list of valid tweets. """
  scored_tweets = []

  for tweet in tweets:
    dt = datetime.strptime(tweet["created_at"].replace("+0000 ", ""), "%a %b %d %H:%M:%S %Y")

    # skip if outside of window
    if dt > stop_time or dt < start_time: continue
    
    score = tweet["favorite_count"] + tweet["retweet_count"]
    scored_tweets.append((score, tweet))

  # sort by score, descending
  scored_tweets.sort(key=lambda tup: tup[0], reverse=True)
  return scored_tweets

def main():
  # init auth and send a simple GET
  client = Client(twitter_apps.API_KEY, twitter_apps.API_SECRET)

  # create a 24 hour window ending 2 hours ago
  now = datetime.utcnow()
  stop_time = now - timedelta(hours=2)
  start_time = now - timedelta(hours=26)  

  for config in getConfig():
    # TODO assuming no more than 50 tweets/day. add ability to get more tweets if necessary
    tweets = client.request("https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=%s&count=50&include_rts=false" % (config[0]))

    scored_tweets = evaluate_tweets(tweets, stop_time, start_time)

    # print results
    print "\nResults for @%s (Limit %s tweets):" % (config[0], config[1])
    for i in range(0, int(config[1])):
      print scored_tweets[i][0], scored_tweets[i][1]["text"]

if __name__ == "__main__":
  main()
