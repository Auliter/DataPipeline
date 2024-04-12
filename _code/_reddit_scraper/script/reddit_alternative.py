import praw
import json
from datetime import datetime
import multiprocessing
from pyspark.sql import SparkSession

reddit = praw.Reddit(
    client_id="baVWOAdQKHhpezDgLJjC2g",
    client_secret="6qe8_KbImEnhI3roWJCxZ7oTkIM0GA",
    user_agent="scrape",
)
current_date = datetime.now().strftime("%Y-%m-%d")
capturedDataNum = 2000
subreddits = ["RealTesla", "TSLA", "teslainvestorsclub", "teslamotors"]

def captureJsonFromSub(subRedditName):
    Json = []
    for submission in reddit.subreddit(subRedditName).new(limit=capturedDataNum):
        instance = {}
        if submission.created_utc:
            dt_object = datetime.fromtimestamp(submission.created_utc)
        else:
            dt_object = datetime.fromtimestamp(submission.created)
        formatted_date = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        instance["date"] = formatted_date
        if submission.author is not None:
            instance["name"] = submission.author.name
        else:
            instance["name"] = "N.A"
        if submission.title:
            instance["rawContent"] = submission.title
        else:
            instance["rawContent"] = submission.selftext
        instance["url"] = submission.url
        instance["num_comments"] = submission.num_comments
        instance["score"] = submission.score
        Json.append(instance)
    df = spark.createDataFrame(Json)
    df.write.json("hdfs://localhost:9000/data/reddit/" + current_date + "/",mode="overwrite")

if __name__ == "__main__":
    spark = SparkSession.builder.appName("MyApp").getOrCreate()
    captureJsonFromSub("RealTesla")
    captureJsonFromSub("TSLA")
    captureJsonFromSub("teslainvestorsclub")
    captureJsonFromSub("teslamotors")
