Do you like some twitter feeds but feel like for every good tweet they send 5 bad ones?  OnlyWorthy will retweet top X tweets (ranked by favorites and retweets) for each user in a list of users over a 24 hour window beginning 2 hours before app execution.

Create a twitter account and app with read/write access. Follow this account to receive the retweets. In my case, I (@ryanjcutter) am following @onlyworthy.

Deployment: Runs on OpenShift with Python 2.7/cron cartridges. Requires tweepy lib. Put .sh in cron's daily folder.
