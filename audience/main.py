from flask import Flask, request, render_template
import tweepy
import logging
from time import time
from sys import argv
from keys import CONSUMER_KEY, CONSUMER_SECRET, USER_KEY, USER_SECRET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)

class TwitterLimit(Exception):
    """Custom exception handling twiter api reset time for the display"""
    def __init__(self, message, reset):
        Exception.__init__(self, "%s [reset in %dsec]" % (message, reset - time()))

class RateLimit(object):
    """This class will check the remaining calls to twitter api on demand and
    raise a TwitterLimit exception if there is no more call available"""
    def __init__(self, limits):
        self.resources = limits["resources"]
        self.rate_limit_context = limits["rate_limit_context"]

    def check_remaining(self, category, name, done = 0):
        current = self.resources[category]["/%s/%s" % (category, name)]
        if current["remaining"] - done <= 0:
            raise TwitterLimit("Limit reached for %s" % (name), current["reset"])

class AuthHandler(object):
    """Simple class that will connect us to twitter api when instantiate"""
    def __init__(self, consumer, consumer_secret, token, token_secret):
        self.auth = tweepy.OAuthHandler(consumer, consumer_secret)
        self.auth.set_access_token(token, token_secret)
        self.api = tweepy.API(self.auth)

class FollowRTProc(object):
    def __init__(self, api, tweetid, organisator):
        self.tweetid = tweetid
        self.api = api
        self.count = 0
        self.orga = organisator
        self.users = []

    def add_retweeter(self, user):
        print "Added user : {}".format(user)
        self.users.append(user)
        self.count += user.followers_count

    def run(self):
        count = self.api.get_status(self.tweetid).retweet_count
        try:
            rts = self.api.retweets(self.tweetid)
        except tweepy.TweepError:
            pass
        else:
            for rt in rts:
                self.add_retweeter(rt.user)
        me = self.api.get_user(screen_name=self.orga)
        self.add_retweeter(me)
        return self.count

    def print_count(self):
        json = {
            "screen_name": [],
            "followers": []
            }
        print "Users : {}".format(self.users)
        for user in self.users:
            json["screen_name"].append(user.screen_name)
            json["followers"].append(user.followers_count)
        return json
            
def process(auth, datas):
    total = 0
    json = {
        "total": 0,
        "users": {"screen_name": [], "followers": []}
        }
    for data in [d for d in datas if d]:
        limits = RateLimit(auth.api.rate_limit_status())
        try:
            limits.check_remaining("statuses", "retweets/:id")
            limits.check_remaining("users", "show/:id")
        except TwitterLimit as e:
            return json, e
        frt = FollowRTProc(auth.api, data["tweetid"], data["orga"])
        json["total"] += frt.run()
        users = frt.print_count()
        json["users"]["screen_name"] += users["screen_name"]
        json["users"]["followers"] += users["followers"]
    return json, None

def parse_url(url):
    try:
        tweetid = url.split('/')[-1]
        orga = url.split('/')[-3]
    except IndexError:
        return None
    return {"tweetid":tweetid, "orga":orga}
    
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and "urls" in request.values:
        urls = request.values["urls"].split('\n')
        auth = AuthHandler(CONSUMER_KEY, CONSUMER_SECRET, USER_KEY, USER_SECRET)
        urls = [u for u in map(parse_url, urls) if u]
        stats, error = process(auth, urls)
        stats["users"] = zip(stats["users"]["screen_name"], stats["users"]["followers"])
        print stats
        nurl = {"total": len(urls), "done": len(stats["users"])}
        return render_template('index.html', stats=stats, error=error, nurl=nurl)
    return render_template('index.html', stats = {}, error=False)


def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()
