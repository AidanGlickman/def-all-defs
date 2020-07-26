import configparser
import tweepy
import re
import requests
from PyDictionary import PyDictionary

dictionary = PyDictionary()


class MyStreamListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        self.me = api.me()

    def on_status(self, tweet):
        processTweet(tweet.id_str)

    def on_error(self, status):
        print("Error detected")


def processTweet(api, config, tweet_id):
    status = api.get_status(tweet_id, tweet_mode='extended')
    # print(status.id_str)
    contents = '\n'.join(
        re.sub('[^a-zA-Z\']', '', status.full_text).split('\n')[1:]).split()
    contents = list(filter(lambda x: x[0] not in ['@', '#', '$'], contents))
    for word in list(dict.fromkeys(contents)):
        try:
            response = requests.get('https://dictionaryapi.com/api/v3/references/collegiate/json/' +
                                    word + '?key=' + config['dictionaryapi.com']['API_KEY'])
            meanings = response.json()[0]['shortdef']
            # print(meanings)
            reply = 'Here\'s the definition of ' + word.capitalize() + '\n' + \
                '\n'.join(meanings)
            # print(reply)
            # print('--------------------------')
            api.update_status(reply,
                              in_reply_to_status_id=status.id_str, auto_populate_reply_metadata=True)
        except:
            pass


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    auth = tweepy.OAuthHandler(
        config['twitter.com']['CONSUMER_KEY'],
        config['twitter.com']['CONSUMER_SECRET'])
    auth.set_access_token(config['twitter.com']['ACCESS_TOKEN'],
                          config['twitter.com']['ACCESS_TOKEN_SECRET'])
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    streamListener = MyStreamListener(api)
    stream = tweepy.Stream(auth=api.auth, listener=streamListener)
    stream.filter(follow=[config['twitter.com']['ACCOUNT_ID']])

    # for tweet in tweepy.Cursor(api.user_timeline, id=config['twitter.com']['ACCOUNT_ID']).items():
    #     processTweet(api, config, tweet.id_str)
    #     input()


main()
