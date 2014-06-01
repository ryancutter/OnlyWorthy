#!/usr/bin/python

"""
onlyworthy.py
~~~~~~~~~~~~~

Weekend project testing the possibility of metering tweets so you only see the best
"""

from sys import argv
from getopt import getopt, GetoptError
from csv import reader
from datetime import datetime, timedelta
from logging import basicConfig, getLogger, INFO
from time import sleep

import twitter_apps
import tweepy

def usage():
  print "usage:"
  print "  -c config file (csv file of twitter_username,desired_num_of_tweets)"

def setupLogger(log, app):
  basicConfig(level=INFO,
              format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
              datefmt='%m-%d-%y %H:%M:%S',
              filename=log,
              filemode='w')
  return getLogger(app)

def get_config(config_file):
  """ read config file and return list of username/# of tweets tuples. """
  with open(config_file, 'rb') as configfile:
    return [row for row in reader(configfile)]

def evaluate_tweets(tweets, stop_time, start_time):
  """ collect and score all tweets in desired time window. return ranked list of valid tweets. """
  scored_tweets = []

  for tweet in tweets:
    # skip if outside of window
    if tweet.created_at > stop_time or tweet.created_at < start_time: continue
    
    score = tweet.favorite_count + tweet.retweet_count
    scored_tweets.append((score, tweet))

  # sort by score, descending
  scored_tweets.sort(key=lambda tup: tup[0], reverse=True)
  return scored_tweets

def main():
  logger = setupLogger("/tmp/onlyworthy.log", "onlyworthy.py")
  logger.info("Starting onlyworthy.py")

  # parse args
  try:
    opts, args = getopt(argv[1:], "c:", ["help"])
  except GetoptError, err:
    print str(err)
    usage()
    exit(2)

  for o, a in opts:
    if o == "-c":
      config_file = a
    else:
      assert False, "unhandled option"

  # init auth
  auth = tweepy.OAuthHandler(twitter_apps.CONSUMER_KEY, twitter_apps.CONSUMER_SECRET)
  auth.set_access_token(twitter_apps.ACCESS_TOKEN, twitter_apps.ACCESS_SECRET)

  twitter_api = tweepy.API(auth)

  # create a 24 hour window ending 2 hours ago
  now = datetime.utcnow()
  stop_time = now - timedelta(hours=2)
  start_time = now - timedelta(hours=26)  

  logger.info("stop_time = " + str(stop_time) + ", start_time = " + str(start_time))

  for config in get_config(config_file):
    logger.info("Pulling @" + config[0])
    # TODO assuming no more than 50 tweets/day. add ability to get more tweets if necessary
    tweets = twitter_api.user_timeline(screen_name=config[0], count=50, include_rts=False)

    scored_tweets = evaluate_tweets(tweets, stop_time, start_time)
    logger.info("Narrowed " + str(len(tweets)) + " down to " + str(len(scored_tweets)))

    # retweet as appropriate 
    for i in range(0, int(config[1])):
      logger.info("Retweeting " + scored_tweets[i][1].text)
      try:
        status = twitter_api.retweet(scored_tweets[i][1].id)

        # sometimes the first try doesn't work, so attempt 5 more times
        retry = 0
        while status.retweeted == False and retry < 5:
          logger.info("retweeted=False, sleeping then retrying")
          sleep(5)
          status = twitter_api.retweet(scored_tweets[i][1].id)
          retry += 1
          
      except tweepy.TweepError, e:
        logger.error("Unable to send tweet - " + scored_tweets[i][1].text)
        logger.error(e.reason)

if __name__ == "__main__":
  main()
