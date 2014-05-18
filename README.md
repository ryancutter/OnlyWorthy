Will return top X tweets (ranked by favorites and retweets) for a user over a 24 hour window beginning 2 hours before app execution.

Working notes.

- create Python 2.7 app on openshift 
- add cron cartridge
- install requests and twitter-application-only-auth python modules
- create twitter app and get API keys 
- to monitor user, add row to config.csv

$ python tweetmeter.py 

Results for @zerohedge (Limit 5 tweets):

133 Household net worth of college grads with student debt: $8,700; net worth of high school grads without student debt: $10,900: Pew

113 Deutsche Bank Scrambles To Raise Capital: Will Sell €8 Billion In Stock At Up To 30% Discount http://t.co/kjzLIeIJmj

92 The Meat Crisis Is Here: Price Of Shrimp Up 61% – 7 Million Pigs Dead – Beef At All-Time High http://t.co/2SEseugJOb

90 77% of Swiss Voters Reject $25 Hourly National Minimum Wage: SRF Projection

83 Fukushima Seawater Radiation Rises To New All Time High http://t.co/EWESZV2HXQ

Results for @nbcsandiego (Limit 3 tweets):

101 How cute are these guys? Find out how else San Diegans are saying thanks to first responders: http://t.co/YWReCW7kEq http://t.co/zW84ySkIkF

58 UPDATE: Poinsettia Fire in Carlsbad now 100% contained - http://t.co/L4IBInTfee

36 How the county is using an app to reunite lost pets with their owners after the #SanDiegoFire evacuations: http://t.co/gBDJ5SK4Su
