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



class TweetByWord(ndb.Model):
    word = ndb.StringProperty()
    recentTweets = ndb.TextProperty(repeated=True)
    timestamp = ndb.TextProperty(repeated=True)
    url = ndb.StringProperty(repeated=True)


class TweetDataStore(webapp2.RequestHandler):

    def post(self):
        keyword = self.request.get('keyword')
        tweetObject = TweetByWord.query(TweetByWord.word==keyword).fetch(1)
        if len(tweetObject) == 0:
            consumer_key = 'XwMBmOrVPc6cFnro2yuu9XoHj'
            consumer_secret = 'IkzDgTmQKP56bWrhAY1cVCKCcv2NFFawlAzTpLvUeQ3iQsd0zx'
            access_token = '59450295-LDdE44hKMcNKp4oZrzpZsuQGci8grQRdtMylLQ3JO'
            access_token_secret = 'wrkJBEWVH8MBXYTdABR4Itj66Zmcclq7PFdH0RhB701Yo'
            t = Twitter(
                auth=OAuth(access_token, access_token_secret, consumer_key, consumer_secret))
            twit = t.search.tweets(q=keyword, count =30)
            tweetArr = []
            tweetTime = []
            tweetURL = [] 
            for i in range(30):
                try:
                    tweetArr.append(twit['statuses'][i]['text'])
                    tweetTime.append(twit['statuses'][i]['created_at'])
                    tweetURL.append(twit['statuses'][i]['id'])
                except IndexError:
                    break   
            tweetData = TweetByWord(word = keyword,recentTweets = tweetArr,timestamp=tweetTime)
            tweetData.put()
            template_values = {
                'key':keyword,
                'tweets':tweetArr,
                'timestamp':tweetTime,
                'url':tweetURL,
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
        tweetObject = TweetByWord.query().fetch()
        template_values = {
            'tweets': tweetObject,
        }
        template = JINJA_ENVIRONMENT.get_template('display.html')
        self.response.write(template.render(template_values))

class CronHourlyUpdate(webapp2.RequestHandler):

    def get(self):
        tweetObject = TweetByWord.query()
        for data in tweetObject.iter():
            consumer_key = 'XwMBmOrVPc6cFnro2yuu9XoHj'
            consumer_secret = 'IkzDgTmQKP56bWrhAY1cVCKCcv2NFFawlAzTpLvUeQ3iQsd0zx'
            access_token = '59450295-LDdE44hKMcNKp4oZrzpZsuQGci8grQRdtMylLQ3JO'
            access_token_secret = 'wrkJBEWVH8MBXYTdABR4Itj66Zmcclq7PFdH0RhB701Yo'
            t = Twitter(
                auth=OAuth(access_token, access_token_secret, consumer_key, consumer_secret))
            twit = t.search.tweets(q=keyword, count =30)
            tweetArr = []
            for i in range(30):
                try:
                    tweetArr.append(twit['statuses'][i]['text'])
                except IndexError:
                    tweetArr.append('')
            temp = data.recentTweets
            data.recentTweets = temp + tweetArr
            data.put()
            self.response.status = 200 
            
class ExternalSearch(webapp2.RequestHandler):
    
    def post(self):  
        keyword = self.request.get('keyword')
        self.redirect('https://twitter.com/search?q='+str(keyword))





app = webapp2.WSGIApplication([
    ('/',TweetDisplay),
    ('/store', TweetDataStore),
    ('/events/.*',CronHourlyUpdate),
    ('/ext',ExternalSearch)
], debug=True)
