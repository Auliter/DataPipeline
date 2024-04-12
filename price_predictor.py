import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import mysql.connector as cnt
from datetime import datetime
from sklearn.linear_model import LinearRegression

class Predictor():
    def __init__(self):
        self.cnx = cnt.connector.connect(user='testUser', password='123456', host='47.250.52.110', database='ModelFeatures')
        #self.cursor = self.cnx.cursor()
        #self.DATETIME_FORMAT = "%Y-%m-%d"
        self.table_name = ["stockPrice", "Sentiment", "TwSentiment"]
        self.Alpha = pd.read_sql(f'SELECT date, close FROM {self.table_name[0]}', self.cnx)
        self.reddit = pd.read_sql(f'SELECT date, score, sentiment FROM {self.table_name[1]}', self.cnx)
        self.twitter = pd.read_sql(f'SELECT date, replyCount, retweetCount, likeCount, sentiment FROM {self.table_name[2]}', self.cnx)
    
    @classmethod
    def get_peak(self, col):
        peak_list = [np.nan for a in col]
        target_list = [np.nan for a in col]
        k = 0
        while True:
            if k + 2 == len(col):
                break
            x2 = col[k]
            if x2 == np.nan:
                k += 1
            else:
                x0 = col[k + 2]
                if x0 == np.nan:
                    break
                x1 = col[k + 1]
                if x0 < x1 and x1 > x2:
                    peak_list[k + 1] = x1
                k += 1
        peak_list = pd.Series(data=peak_list, index=col.index)
        peak_list = peak_list.shift(1).fillna(method="ffill")
        target_list = [col[i] / peak_list[i] - 1 for i in range(len(col))]
        return target_list
    
    def datapreprocess(self):
        # Constructing Factors
        self.Alpha.set_index(self.Alpha['date'], inplace=True)
        self.Alpha.sort_index(ascending=True, inplace=True)
        self.momentum = self.Alpha / self.Alpha.shift(20)  # momentum factor
        high_17 = self.Alpha.rolling(window=17, min_periods=17, closed="left").max()
        low_17 = self.Alpha.rolling(window=17, min_periods=17, closed="left").min()
        h_l = high_17 - low_17
        h_l = h_l.replace(0, np.nan)
        self.percent = (self.Alpha - low_17) / h_l  # high_low_factor
        return_daily = self.Alpha / self.Alpha.shift(1) - 1
        self.max_20 = return_daily.rolling(window=20, min_periods=20, closed="left").max() # max_factor
        self.RL = self.Alpha.apply(self.get_peak) # RL factor

        # define reddit sentiment factor
        self.reddit = self.reddit.dropna().reset_index(drop=True)
        self.reddit['date'] = self.reddit['date'].apply(lambda x: x[:10])  # "%Y-%m-%d"
        self.reddit['score'] = self.reddit['score'].apply(lambda x: int(x))
        self.reddit['sentiment'] = self.reddit['sentiment'].apply(lambda x: int(x))
        self.reddit['senti_reddit'] = self.reddit['score'] * self.reddit['sentiment']  # This factor can be considered to be uploaded to the cloud
        self.reddit = self.reddit.drop(['score', 'sentiment'], axis=1)
        self.reddit_sum = self.reddit.groupby('date').sum()
        self.reddit_sum.set_index(self.reddit['date'], inplace=True)
        self.reddit_sum.sort_index(ascending=True, inplace=True)

        # define twitter sentiment factor
        self.twitter = self.twitter.dropna().reset_index(drop=True)
        self.twitter['date'] = self.twitter['date'].apply(lambda x: x[:10])  # "%Y-%m-%d"
        self.twitter['replyCount'] = self.twitter['replyCount'].apply(lambda x: int(x))
        self.twitter['retweetCount'] = self.twitter['retweetCount'].apply(lambda x: int(x))
        self.twitter['likeCount'] = self.twitter['likeCount'].apply(lambda x: int(x))
        self.twitter['sentiment'] = self.twitter['sentiment'].apply(lambda x: int(x))
        self.twitter['senti_twitter'] = self.twitter['likeCount'] * self.twitter['sentiment']  # This factor can be considered to be uploaded to the cloud
        self.twitter = self.twitter.drop(['replyCount', 'retweetCount', 'likeCount', 'sentiment'], axis=1)
        self.twitter_sum = self.twitter.groupby('date').sum()
        self.twitter_sum.set_index(self.twitter['date'], inplace=True)
        self.twitter_sum.sort_index(ascending=True, inplace=True)

        # concatenate
        self.X = pd.concat([self.momentum, self.percent, self.max_20, self.RL, self.reddit_sum, self.twitter_sum], axis=1, join="inner")

    def close_connection(self):
        #self.cursor.close()
        self.cnx.close()

    def predict(self):
        Y = self.Alpha.shift(-1)
        self.regr = LinearRegression().fit(self.X[:-1], Y[:-1])
        P = self.regr.predict(self.X.iloc[-1,:])    
        return P[0]

    def visualize(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.X.index, self.X['close'], label='TSLA Close Price')
        plt.plot(self.X.index, self.X['senti_reddit'], label='Reddit Sentiment')
        plt.plot(self.X.index, self.X['senti_twitter'], label='Twitter Sentiment')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    predictor = Predictor()
    P_tom = predictor.predict()
    predictor.close_connection()
    print("We guess tomorrow TSLA close price is:", P_tom)
    predictor.visualize()