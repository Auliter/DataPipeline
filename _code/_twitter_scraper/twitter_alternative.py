"""
This example shows how to use twscrape to complete some queries in parallel.
To limit the number of concurrent requests, see examples/parallel_search_with_limit.py
"""
import asyncio
import twscrape
import json
from pyspark.sql import SparkSession
from datetime import datetime

spark = SparkSession.builder.appName("MyApp").getOrCreate()
current_date = datetime.now().strftime("%Y-%m-%d")
file_path = "hdfs://localhost:9000/data/tweets/"+current_date
result = {}
async def worker(api: twscrape.API, q: str):
    tweets = []
    try:
        async for doc in api.search(q,limit=2):
            tweets.append(doc)
    except Exception as e:
        print(e)
    finally:
        return tweets_to_json(tweets)

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

async def main():
    api = twscrape.API()
    await api.pool.add_account("@tempforqf5214", "dB~Q^!c/na8v.6+", "mailforqf5214@yahoo.com", "Mkun4?Y.QanNig%") #XuZiyi
    await api.pool.add_account("@CaiSenti62009", "istKySg6kc6p77:", "yuze_cai@yahoo.com", "/LMqTK2Z&yMi4hX") #Caiyuze
    await api.pool.add_account("@yngwnd1267223", "e7C_BsHEu5iLceX", "dylanywd@myyahoo.com", "_HASz-Azs!6x26Z") #YangWendi
    await api.pool.add_account("@yayoooooya", "ilikebbg5!", "hooyayooh@myyahoo.com", "ilikebbg5!") #MaYufei
    await api.pool.add_account("@AnyaTaylor97390", "Cms123456", "anyatalorjoyhaha@gmail.com", "Cms123456") #YangYihang
    await api.pool.add_account("@tianti49373", "cms123456", "chentiantian2222@gmail.com", "cms123456") #YangYihang
    await api.pool.login_all()

    queries = ["tesla battery", "tesla innovation", "tesla excited", "tesla performance", "tesla up", \
             "tesla electric", "tesla product", "tesla elon", "tesla buy"]
    results = await asyncio.gather(*(worker(api, q) for q in queries))
    combined = dict(zip(queries, results))
    result = combined
    for k, v in combined.items():
        jsonDataList = []
        jsonDataList.append(v)
        jsonRDD = spark.sparkContext.parallelize(jsonDataList)
        df = spark.read.json(jsonRDD)
        df.write.json(file_path,mode="overwrite")


if __name__ == "__main__":
    asyncio.run(main())
