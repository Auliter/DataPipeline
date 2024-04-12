import mysql.connector as cnt
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
import warnings
from datetime import datetime
import pandas as pd
import sys

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
directory = "hdfs://localhost:9000/data/alphavantage/"+current_date
df = spark.read.json(directory)
df.show()
data_collect = df.collect()

cnx = cnt.connect(user='testUser',password='123456',host='47.250.52.110',database='ModelFeatures')
mycursor = cnx.cursor()
for row in data_collect:
    sql = "INSERT INTO stockPrice (close,date,high,low,open,symbol) VALUES (%s,%s,%s,%s,%s,%s)"
    val = (row["close"],row["date"],row["high"],row["low"],row["open"],row["symbol"])
    try:
        mycursor.execute(sql,val)
        cnx.commit()
    except:
        print("Record already exist")
