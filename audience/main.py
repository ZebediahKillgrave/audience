from flask import Flask, request, render_template
import tweepy
from tweepy import TweepError
from time import time
from keys import CONSUMER_KEY, CONSUMER_SECRET, USER_KEY, USER_SECRET

app = Flask(__name__)

class TwitterLimit(Exception):
    """
    Custom exception handling twiter api reset time for the display
    """
    def __init__(self, message, reset):
        Exception.__init__(self, "%s [reset in %dsec]" % (message, reset - time()))

class RateLimit(object):
    """
    This class will check the remaining calls to twitter api on demand and
    raise a TwitterLimit exception if there is no more call available
    """
    def __init__(self, limits):
        self.resources = limits["resources"]
        self.rate_limit_context = limits["rate_limit_context"]

    def check_remaining(self, category, name, done = 0):
        current = self.resources[category]["/%s/%s" % (category, name)]
        if current["remaining"] - done <= 0:
            raise TwitterLimit("Limit reached for %s" % (name), current["reset"])

class AuthHandler(object):
    """
    Simple class that will connect us to twitter api when instantiate
    """
    def __init__(self, consumer, consumer_secret, token, token_secret):
        self.auth = tweepy.OAuthHandler(consumer, consumer_secret)
        self.auth.set_access_token(token, token_secret)
        self.api = tweepy.API(self.auth)


class Tweet(object):
    def __init__(self, tweetid, user, api):
        self.api = api
        self.user = user
        self.tweetid = tweetid
        self.user_followers = api.get_user(screen_name=user).followers_count
        self.retweets = api.retweets(tweetid)
    
    def compute_audience(self):
        audience = 0
        for retweet in self.retweets:
            audience += retweet.user.followers_count
        return audience + self.user_followers

class URL(object):
    def __init__(self, url):
        self.url = url
        try:
            self.tweetid = url.split('/')[-1]
            self.user = url.split('/')[-3]
        except IndexError:
            self.tweetid = None
            self.user = None

class Process(object):
    def __init__(self, urls, auth):
        self.urls = map(URL, urls)
        self.auth = auth
    
    def run(self):
        total = 0
        for url in self.urls:
            if url.tweetid and url.user:
                try:
                    total += Tweet(url.tweetid, url.user, self.auth.api).compute_audience()
                except TweepError:
                    break
        return total

@app.route('/', methods=['GET', 'POST'])
def index():
    stats = {}
    if request.method == 'POST' and "urls" in request.values:
        urls = [u.strip() for u in request.values["urls"].split('\n')]
        print urls
        auth = AuthHandler(CONSUMER_KEY, CONSUMER_SECRET, USER_KEY, USER_SECRET)
        stats["total"] = Process(urls, auth).run()
    return render_template('index.html', stats=stats)


def main():
    app.run(host='0.0.0.0', debug=True)

if __name__ == "__main__":
    main()
