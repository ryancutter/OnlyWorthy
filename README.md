Do you like some twitter feeds but feel like for every good tweet they send 5 bad ones?  OnlyWorthy will retweet top X tweets (quantified by amount of favorites and retweets) for each account over a 24 hour trailing window.

Create a twitter account and app with read/write access and add credentials to twitter\_apps.py. Follow this account to receive the retweets. In my case, I (@ryanjcutter) am following @onlyworthy.

Deployment: Runs on OpenShift with Python 2.7 and cron cartridges. Requires tweepy lib. Put .sh in cron's daily folder.
