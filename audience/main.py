import tweepy
import logging
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
        me = self.api.get_user(screen_name=self.orga)
        self.add_retweeter(me)

    def print_count(self):
        for user in self.users:
            print "User {} has {} followers.".format(user.screen_name, user.followers_count)
        print "_______________________________________\n"
        print "That's a total of {} retweets.".format(len(self.users) - 1)
        print "Tweet {} has an audience of about {} people.".format(self.tweetid, self.count)

def main():
    if len(argv) != 2:
        print ("Usage: audience [link]\n"
               "Example: audience https://twitter.com/SDEntrepreneurs/status/431412241150529536")
        return
    tweetid = argv[1].split('/')[-1]
    orga = argv[1].split('/')[-3]
    auth = AuthHandler(CONSUMER_KEY, CONSUMER_SECRET, USER_KEY, USER_SECRET)
    frt = FollowRTProc(auth.api, tweetid, orga)
    limits = RateLimit(auth.api.rate_limit_status())
    limits.check_remaining("statuses", "retweets/:id")
    limits.check_remaining("users", "show/:id")
    frt.run()
    frt.print_count()

if __name__ == "__main__":
    main()
