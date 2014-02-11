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

First you need to fill the keys.py file with your info :

```shell
cp keys.py.sample keys.py
```

Don't forget to paste your own keys in each variable without changing their name.
If you do you won't be able to connect to the Twitter API.

Then install the package in a virtualenv :

```shell
$ virtualenv env --distribute
$ source env/bin/acivate
(env)$ pip install -e .
```

Now you should have successfully installed the package !
If you want it in your main python path just execute the last command : `pip install -e .`.

# Example

```shell
$ audience -f urls.example --not-me
```

```shell
$ audience https://twitter.com/SDEntrepreneurs/status/430989433111060480 -v
```

```shell
$ audience -f urls.example --not-me -v
```

```shell
$ audience -f urls.example
```

# Man

#### NAME

audience - approximate audience of a given tweet/set of tweets

#### SYNOPSIS

audience tweet_url [-v] [--not-me]

audience -f filename [-v] [--not-me]

#### DESCRIPTON

In the 1st form, uses the tweet_url to calculate the audience. It must be a direct link to a tweet. In the 2nd form, it does the same thing for every link in the file passed as parameter. There must be one link per line and each link must be a direct link to a tweet.
Because of twitter rate API limits you can only use this script for 15 urls / 15 minutes.

#### OPTIONS

-v	 : verbose mode

--not-me : don't count own followers

#### AUTHOR

Written by Florent Espanet
