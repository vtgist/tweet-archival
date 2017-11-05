import os
import logging
from twitter import *
import json

from flask import Flask, render_template, request
from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)



class TweetByHashtag(ndb.Model):
    hashtag = ndb.StringProperty()
    recentTweets = ndb.TextProperty(repeated=True)


class TweetDataStore(webapp2.RequestHandler):

    def post(self):
        keyword = self.request.get('keyword')
        keytag = str('#')+keyword
        tweetObject = TweetByHashtag.query(TweetByHashtag.hashtag==keyword).fetch(1)
        if len(tweetObject) == 0:
            consumer_key = 'XwMBmOrVPc6cFnro2yuu9XoHj'
            consumer_secret = 'IkzDgTmQKP56bWrhAY1cVCKCcv2NFFawlAzTpLvUeQ3iQsd0zx'
            access_token = '59450295-LDdE44hKMcNKp4oZrzpZsuQGci8grQRdtMylLQ3JO'
            access_token_secret = 'wrkJBEWVH8MBXYTdABR4Itj66Zmcclq7PFdH0RhB701Yo'
            t = Twitter(
                auth=OAuth(access_token, access_token_secret, consumer_key, consumer_secret))
            twit = t.search.tweets(q=keytag, count =30)
            tweetArr = []
            for i in range(30):
                try:
                    tweetArr.append(twit['statuses'][i]['text'])
                except IndexError:
                    tweetArr.append('')
            tweetData = TweetByHashtag(hashtag = keyword,recentTweets = tweetArr)
            tweetData.put()
            template_values = {
                'key':keyword,
                'tweets':tweetArr,
            }
            template = JINJA_ENVIRONMENT.get_template('tweet.html')
            self.response.write(template.render(template_values))
        else:
            template_values = {
                'tweets': tweetObject,
            }
            template = JINJA_ENVIRONMENT.get_template('existing_tweet.html')
            self.response.write(template.render(template_values))
            


class TweetDisplay(webapp2.RequestHandler):

    def get(self):
        tweetObject = TweetByHashtag.query().fetch()
        template_values = {
            'tweets': tweetObject,
        }
        template = JINJA_ENVIRONMENT.get_template('display.html')
        self.response.write(template.render(template_values))
#TODO
class CronHourlyUpdate(webapp2.RequestHandler):
    def get(self):
        tweetObject = TweetByHashtag.query().fetch()
        for tweet in tweetObject:
            self.response.write(tweet.hashtag)
            for t in tweet.recentTweets:
                self.response.write(tweet.recentTweets)
                self.response.write('\n')

        
app = webapp2.WSGIApplication([
    ('/',TweetDisplay),
    ('/store', TweetDataStore),
    ('/events/.*',CronHourlyUpdate)
], debug=True)

