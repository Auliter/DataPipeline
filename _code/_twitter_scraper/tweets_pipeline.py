import json
import os

def tweet_selected_dict(tweet):
    # Select only some features from the tweet object
    # turn the tweet class into a dictionary
    # FEEL FREE TO CHANGE THE FEATURES!
    processed_tweet = {
        "id": tweet.id,
        "url": tweet.url,
        "date": tweet.date.isoformat() if tweet.date else None,
        "lang": tweet.lang,
        "rawContent": tweet.rawContent,
        "replyCount": tweet.replyCount,
        "retweetCount": tweet.retweetCount,
        "likeCount": tweet.likeCount,
        "quoteCount": tweet.quoteCount,
        "hashtags": tweet.hashtags,
    }
    return processed_tweet

def tweets_to_json(tweets):
    # Convert the list of tweet objects into a JSON string
    tweets_dicts = [tweet_selected_dict(tweet) for tweet in tweets]
    tweets_json = json.dumps(tweets_dicts, ensure_ascii=False, indent=4)
    return tweets_json

def tweets_json_to_file(json_str, file_path, filename):
    full_path = os.path.join(file_path, filename)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(json_str)
