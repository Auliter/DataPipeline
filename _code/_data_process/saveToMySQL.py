import mysql.connector as cnt
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
import warnings
from datetime import datetime
import pandas as pd
import sys


if len(sys.argv)<2:
    sys.exit()
spark = SparkSession.builder \
    .master("local[4]") \
    .appName("Spark NLP Example") \
    .config("spark.driver.memory", "8G") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.kryoserializer.buffer.max", "2000M") \
    .config("spark.driver.maxResultSize", "2G") \
    .getOrCreate()
current_date = datetime.now().strftime("%Y-%m-%d")
#current_date = "2024-04-09"
directory = "hdfs://localhost:9000/data/"+sys.argv[1]+"/"+current_date+"/test_data"
df = spark.read.csv(directory,multiLine=True)
df.show()
data_collect = df.collect()

cnx = cnt.connect(user='testUser',password='123456',host='47.250.52.110',database='ModelFeatures')
mycursor = cnx.cursor()
for row in data_collect[1:]:
    if sys.argv[1] == "tweets":
        sql = "INSERT INTO TwSentiment (date, rawContent, url, replyCount, retweetCount, likeCount, sentiment) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        val = (row["_c0"],row["_c1"],row["_c2"],row["_c3"],row["_c4"],row["_c5"],row["_c6"])
    else:
        sql = "INSERT INTO Sentiment (date, url, numOfComments, score, sentiment, rawContent) VALUES (%s,%s,%s,%s,%s,%s)"
        val = (row["_c0"],row["_c2"],row["_c3"],row["_c4"],row["_c5"],row["_c1"])
    try:
        mycursor.execute(sql,val)
        cnx.commit()
    except:
        print("Record already exist")
