import asyncio
import time
import twscrape

from datetime import datetime, timedelta
from tweets_pipeline import tweets_to_json, tweets_json_to_file
from pyspark.sql import SparkSession

current_date = datetime.now().strftime("%Y-%m-%d")
spark = SparkSession.builder.appName("MyApp").getOrCreate()
db_path = "../../_data/_twitter/accounts.db"
file_path = "hdfs://localhost:9000/data/tweets/"+current_date
DATETIME_FORMAT = "%Y-%m-%d"
BEGIN_DATE = (datetime.today() - timedelta(days=1)).strftime(DATETIME_FORMAT)
END_DATE = datetime.today().strftime(DATETIME_FORMAT)
KEY_WORDS = ["tesla battery", "tesla innovation", "tesla excited", "tesla performance", "tesla up", \
             "tesla electric", "tesla product", "tesla elon", "tesla buy"]

# vladkens/twscrape
# https://github.com/vladkens/twscrape/tree/00a8e07b43c1fbbea95566cc3aae95db76cd4ae3
async def worker(queue: asyncio.Queue, api: twscrape.API):
    while True:
        query = await queue.get()

        try:
            # change search tab (product), can be: Top, Latest (default), Media
            # limit supposes to be the number of tweets to get, but it's not working properly
            tweets = await twscrape.gather(api.search(query, limit=20, kv={"product": "Top"}))
            print(f"{query} - {len(tweets)} - {int(time.time())}")
            tweets_json = tweets_to_json(tweets)
            jsonDataList = []
            jsonDataList.append(tweets_json)
            jsonRDD = spark.sparkContext.parallelize(jsonDataList)
            df = spark.read.json(jsonRDD)
            df.write.json(file_path,mode="overwrite")
        except Exception as e:
            print(f"Error on {query} - {type(e)}")
        finally:
            queue.task_done()


async def main():
    api = twscrape.API(db_path)
    await api.pool.login_all()

    #queries = ["elon musk since:2023-01-01 until:2023-05-31", "tesla", "spacex", "neuralink", "boring company"]
    queries = [f"{_} since:{BEGIN_DATE} until:{END_DATE}" for _ in KEY_WORDS]
    queue = asyncio.Queue()

    # limit concurrency here 1 concurrent requests at time
    workers_count = 2
    workers = [asyncio.create_task(worker(queue, api)) for _ in range(workers_count)]
    for q in queries:
        queue.put_nowait(q)

    await queue.join()
    for worker_task in workers:
        worker_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
