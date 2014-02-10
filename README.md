# Audience

Evaluates a given tweet audience, for example :
```shell
$ audience https://twitter.com/volent_test/status/413247291634364416
User volent_ has 29 followers.
User volent_test has 3 followers.
_______________________________________

That's a total of 1 retweets.
Tweet 413247291634364416 has an audience of about 32 people.
```

# How To Use

If you've tried to launch the main.py without doing the following step
you probably stumbled across an ImportError telling you to come here.
You just have to execute this command :
```shell
cp keys.py.sample keys.py
```
And then you can paste your own keys in each variable without changing their name.
If you don't you won't be able to connect to the Twitter API.

# Man

### NAME
	audience - approximate audience of a given tweet/set of tweets

### SYNOPSIS
	audience tweet_url [-v] [--not-me]
	audience -f filename [-v] [--not-me]

### DESCRIPTON
	In the 1st form, uses the tweet_url to calculate the audience. It must be a direct link to a tweet. In the 2nd form, it does the same thing for every link in the file passed as parameter. There must be one link per line and each link must be a direct link to a tweet.
	Because of twitter rate API limits you can only use this script for 15 urls / 15 minutes.

### OPTIONS
      -v	
      		verbose mode
      --not-me
		don't count own followers

### AUTHOR
	Written by Florent Espanet