import json
import requests
from datetime import datetime, timedelta
from pyspark.sql import SparkSession

class Utf8Encoder(object):

    def __init__(self, fp):
        self.fp = fp

    def write(self, data):
        if not isinstance(data, bytes):
            data = data.encode('utf-8')
        self.fp.write(data)

def get_stock_data(symbol, api_key):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    return data

def filter_two_years_data(data):
    today = datetime.now()
    two_years_ago = today - timedelta(days=2*365)
    filtered_data = {}
    for date, info in data['Time Series (Daily)'].items():
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        if date_obj >= two_years_ago:
            filtered_data[date] = info
    return {'Meta Data': data['Meta Data'], 'Time Series (Daily)': filtered_data}

def json_to_list(data, symbol):
    data_list = []
    for date, values in data['Time Series (Daily)'].items():
        day_data = {
            "symbol": symbol,
            "date": date,
            "open": float(values["1. open"]),
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": float(values["4. close"])
        }
        data_list.append(day_data)
    return data_list

if __name__ == "__main__":
    current_date = datetime.now().strftime("%Y-%m-%d")
    spark = SparkSession.builder.appName("MyApp").getOrCreate()
    symbols = ["TSLA"]  # List of stock symbols
    api_key = "YOUR_API_KEY"  #API key: L848G6PEVRFGE1LR
    for symbol in symbols:
        stock_data = get_stock_data(symbol, api_key)
        filtered_data = filter_two_years_data(stock_data)
        tsla_data_list = json_to_list(filtered_data, symbol)
        filename = f"{symbol}_data_2Y.json"
        df = spark.createDataFrame(tsla_data_list)
        df.write.json("hdfs://localhost:9000/data/alphavantage/"+current_date+"/", mode="overwrite")
        print(len(tsla_data_list))
        print(f"Data for {symbol} has been saved to {filename}")
