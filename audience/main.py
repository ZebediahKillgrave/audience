from flask import Flask, request, render_template, session, url_for, redirect
import tweepy
from tweepy import TweepError
from time import time
from keys import CONSUMER_KEY, CONSUMER_SECRET
import redis

app = Flask(__name__)
app.debug = True
app.secret_key = 'bisous<3'
redis = redis.Redis('localhost')

class TwitterLimit(Exception):
    """
    Custom exception handling twiter api reset time for the display
    """
    def __init__(self, message, reset):
        Exception.__init__(self, "%s [reset dans %dsec]" % (message, reset - time()))

class RateLimit(object):
    """
    This class will check the remaining calls to twitter api on demand and
    raise a TwitterLimit exception if there is no more call available

    Param is api.rate_limti_status()
    """
    def __init__(self, limits):
        self.resources = limits["resources"]
        self.rate_limit_context = limits["rate_limit_context"]

    def check_remaining(self, category, name, done = 0):
        current = self.resources[category]["/%s/%s" % (category, name)]
        if current["remaining"] - done <= 0:
            raise TwitterLimit("Rate limit atteint pour %s" % (name), current["reset"])

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
                    limit = RateLimit(self.auth.api.rate_limit_status())
                    limit.check_remaining('statuses', 'retweets/:id')
                    # limit.check_remaining('users', 'show')
                    total += Tweet(url.tweetid, url.user, self.auth.api).compute_audience()
                except TwitterLimit as e:
                    return total, e
        return total, ""

class Auth(object):
    def __init__(self, consumer_key, consumer_secret, user_key, user_secret):
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(user_key, user_secret)
        self.api = None
        self.connect()

    def connect(self):
        self.api = tweepy.API(self.auth)

@app.route('/login')
def login():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.secure = True
    url = auth.get_authorization_url()
    session['tokens'] = (auth.request_token.key, auth.request_token.secret)
    return redirect(url)

@app.route('/callback')
def callback():
    if 'oauth_verifier' in request.values:
        verifier = request.values['oauth_verifier']
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        token = session['tokens']
        auth.set_request_token(token[0], token[1])
        auth.get_access_token(verifier)
        key, secret = auth.access_token.key, auth.access_token.secret
        session['twitter_auth'] = (key, secret)
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    if 'twitter_auth' in session:
        del session['twitter_auth']
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    stats = {}
    error = ""
    if 'twitter_auth' not in session:
        return render_template('index.html', stats=stats, user=None)
    auth = Auth(CONSUMER_KEY, CONSUMER_SECRET, 
                session['twitter_auth'][0], session['twitter_auth'][1])
    if request.method == 'POST' and "urls" in request.values:
        urls = [u.strip() for u in request.values["urls"].split('\n')]
        stats["total"], error = Process(urls, auth).run()
    return render_template('index.html', stats=stats, user=auth.api.me(), error=error)



def main():
    app.run(host='0.0.0.0', debug=True)

if __name__ == "__main__":
    main()
