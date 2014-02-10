import tweepy
import logging
from time import time
from sys import argv
from keys import CONSUMER_KEY, CONSUMER_SECRET, USER_KEY, USER_SECRET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        self.users.append(user)
        self.count += user.followers_count

    def run(self):
        count = self.api.get_status(self.tweetid).retweet_count
        rts = self.api.retweets(self.tweetid, count)
        for rt in rts:
            self.add_retweeter(rt.user)
        if "--not-me" not in argv:
            me = self.api.get_user(screen_name=self.orga)
            self.add_retweeter(me)

    def print_count(self):
        if "-v" in argv:
            for user in self.users:
                print "User {} has {} followers.".format(user.screen_name, user.followers_count)
                print "_______________________________________\n"
            print "That's a total of {} retweets.".format(len(self.users) - 1)
        print "Tweet {} has an audience of about {} people.".format(self.tweetid, self.count)

def usage():
    print ("Usage: audience [link]\n"
           "Example: audience https://twitter.com/SDEntrepreneurs/status/431412241150529536")
    exit(1)

def process(auth, datas):
    for data in datas:
        limits = RateLimit(auth.api.rate_limit_status())
        limits.check_remaining("statuses", "retweets/:id")
        limits.check_remaining("users", "show/:id")
        frt = FollowRTProc(auth.api, data["tweetid"], data["orga"])
        frt.run()
        frt.print_count()

def parse_url(url):
    tweetid = url.split('/')[-1]
    orga = url.split('/')[-3]
    return {"tweetid":tweetid, "orga":orga}
    
def get_urls_from_filename(filename):
    urls = []
    print "Starting audience computing for :"
    with open(filename) as f:
        for url in f.readlines():
            urls.append(url.strip("\n"))
            if "-v" in argv:
                print urls[-1]
    return urls

def main():
    if len(argv) < 2 or (argv[1] == "-f" and len(argv) < 3):
        usage()
    if argv[1] == "-f":
        urls = get_urls_from_filename(argv[2])
    else:
        urls = [argv[1]]
    auth = AuthHandler(CONSUMER_KEY, CONSUMER_SECRET, USER_KEY, USER_SECRET)
    try:
        process(auth, map(parse_url, urls))
    except TwitterLimit as e:
        print str(e)


if __name__ == "__main__":
    main()
