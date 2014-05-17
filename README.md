Working notes.

- create Python 2.7 app on opensource
- add cron cartridge
- install requests and twitter-application-only-auth modules
- create twitter app and get API keys 

> python app-deployments/current/repo/tweetmeter.py 
'''json
{
    "contributors":null,
    "coordinates":null,
    "created_at":"Sun May 11 04:29:18 +0000 2014",
    "entities":{
        "hashtags":[],
        "symbols":[],
        "urls":[
            {
                "display_url":"youtube.com/watch?v=tEm0US\u2026",
                "expanded_url":"https://www.youtube.com/watch?v=tEm0USdF-70",
                "indices":[
                    108,
                    131
                ],
                "url":"https://t.co/c9hPqfu7Yu"
            }
        ],
        "user_mentions":[
            {
                "id":16736130,
                "id_str":"16736130",
                "indices":[
                    37,
                    50
                ],
                "name":"Oliver Gierke",
                "screen_name":"olivergierke"
            }
        ]
    },
    "favorite_count":0,
    "favorited":false,
    "geo":null,
    "id":465347894480891906,
    "id_str":"465347894480891906",
    "in_reply_to_screen_name":null,
    "in_reply_to_status_id":null,
    "in_reply_to_status_id_str":null,
    "in_reply_to_user_id":null,
    "in_reply_to_user_id_str":null,
    "lang":"en",
    "place":null,
    "possibly_sensitive":false,
    "retweet_count":0,
    "retweeted":false,
    "source":"web",
    "text":"Bummed I've only just now discovered @olivergierke's excellent talk \"Whoops! Where did my architecture go?\" https://t.co/c9hPqfu7Yu",
    "truncated":false,
    "user":{
        "contributors_enabled":false,
        "created_at":"Sat Dec 11 22:26:01 +0000 2010",
        "default_profile":true,
        "default_profile_image":false,
        "description":"Software Engineer at Semantic Research, Inc. Tweets my own. Sometimes @junecutter makes me pancakes.",
        "entities":{
            "description":{
                "urls":[]
            },
            "url":{
                "urls":[
                    {
                        "display_url":"ryancutter.org",
                        "expanded_url":"http://ryancutter.org",
                        "indices":[
                            0,
                            22
                        ],
                        "url":"http://t.co/Jc7tZalGdH"
                    }
                ]
            }
        },
        "favourites_count":67,
        "follow_request_sent":null,
        "followers_count":36,
        "following":null,
        "friends_count":88,
        "geo_enabled":false,
        "id":225567774,
        "id_str":"225567774",
        "is_translation_enabled":false,
        "is_translator":false,
        "lang":"en",
        "listed_count":1,
        "location":"San Diego, CA",
        "name":"Ryan Cutter",
        "notifications":null,
        "profile_background_color":"C0DEED",
        "profile_background_image_url":"http://abs.twimg.com/images/themes/theme1/bg.png",
        "profile_background_image_url_https":"https://abs.twimg.com/images/themes/theme1/bg.png",
        "profile_background_tile":false,
        "profile_banner_url":"https://pbs.twimg.com/profile_banners/225567774/1373752601",
        "profile_image_url":"http://pbs.twimg.com/profile_images/378800000130134079/395106bcb39506b6be10d062872dc954_normal.jpeg",
        "profile_image_url_https":"https://pbs.twimg.com/profile_images/378800000130134079/395106bcb39506b6be10d062872dc954_normal.jpeg",
        "profile_link_color":"0084B4",
        "profile_sidebar_border_color":"C0DEED",
        "profile_sidebar_fill_color":"DDEEF6",
        "profile_text_color":"333333",
        "profile_use_background_image":true,
        "protected":false,
        "screen_name":"ryanjcutter",
        "statuses_count":205,
        "time_zone":"Arizona",
        "url":"http://t.co/Jc7tZalGdH",
        "utc_offset":-25200,
        "verified":false
    }
}
'''
