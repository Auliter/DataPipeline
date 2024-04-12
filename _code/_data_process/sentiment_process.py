import os
import sys
from datetime import datetime
from sparknlp.base import DocumentAssembler
from sparknlp.annotator import Tokenizer, RoBertaForSequenceClassification, DistilBertForSequenceClassification
from pyspark.ml import Pipeline, PipelineModel
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
import warnings

# If TypeError: 'JavaPackage' object is not callable, run this:
# spark-submit --packages com.johnsnowlabs.nlp:spark-nlp_2.12:5.3.3 process.py

# In default, Label 1 is positive, Label 0 is negative


# test on 4 local CPUs
spark = SparkSession.builder \
    .master("local[4]") \
    .appName("Spark NLP Example") \
    .config("spark.driver.memory", "8G") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.kryoserializer.buffer.max", "2000M") \
    .config("spark.driver.maxResultSize", "2G") \
    .config("spark.jars.packages", "com.johnsnowlabs.nlp:spark-nlp_2.12:5.3.3") \
    .getOrCreate()


class DataPaths:
    def __init__(self, base_directory, sub_directory=None, file_type="json", file_name=None):
        # make the read file path in hadoop like "base_directory/sub_directory/*.file_type"
        # sub_directory is the file name exclude the file type
        self.base_directory = base_directory # directory for all the raw data
        self.sub_directory = sub_directory # directory for different sources
        self.file_type = file_type
        if file_name:
            self.data_path = os.path.join(base_directory, file_name)
        else:
            if sub_directory:
                self.data_path = os.path.join(base_directory, sub_directory, f"*.{file_type}")
                self.data_save_path = os.path.join(base_directory, sub_directory)
            else:
                self.data_path = os.path.join(base_directory, f"*.{file_type}")
                self.data_save_path = os.path.join(base_directory)


class DataProcess(DataPaths):
    def __init__(self, base_directory, sub_directory=None, file_type="json", file_name=None):
        super().__init__(base_directory, sub_directory, file_type, file_name)
        self.model_path = "sentiment_model"
        self.raw_data = None
        self.data = None
        self.sentiment_model = None
        self.labeled_data = None

    def read_file(self):
        # read data file as a dataframe
        self.raw_data = spark.read.json(self.data_path, multiLine=True)

    def get_content(self, key="rawContent"):
        if "tweets" in self.data_path:
            self.data = self.raw_data.select("date", key, "url", "replyCount", "retweetCount", "likeCount")
        elif "reddit" in self.data_path:
            self.data = self.raw_data.select("date", key, "url", "num_comments", "score")
    def load_model(self):
        self.sentiment_model = PipelineModel.load(self.model_path)

    def predict_context_sentiment(self):
        self.read_file()
        self.get_content()
        self.load_model()
        self.labeled_data = self.sentiment_model.transform(self.data)

    def reorganize_data(self, input_col='class', output_col='sentiment', drop_cols=None):
        # extract LABEL in class into sentiment
        # drop cols document, token, and class
        self.labeled_data = self.labeled_data.withColumn(
            output_col,
            when(col(input_col).getItem(0)["result"] == "LABEL_1", 1)
            .when(col(input_col).getItem(0)["result"] == "LABEL_0", 0)
            .otherwise(None)  # Use None or another value for cases that don't match LABEL_1 or LABEL_0
        )
        if drop_cols is None:
            drop_cols = ["document", "token", "class"]
            self.labeled_data = self.labeled_data.drop(*drop_cols)

    def save_data(self, file_name):
        self.reorganize_data()
        file_path = os.path.join(self.data_save_path, file_name)
        self.labeled_data.write.csv(file_path, header=True,mode="overwrite")
        dataCollect = self.labeled_data.collect()
        for row in dataCollect:
            print("lol"+row)
            print("lol"+row[date])
            
class TrainModel:
    def __init__(self, data_process):
        self.data_process = data_process
        self.model_path = "sentiment_model"
        self.train_data = None
        self.nlp_pipeline = None
        self.model = None

    def fit_pretrained_model(self):
        self.data_process.read_file()
        self.data_process.get_content()
        self.train_data = self.data_process.data

        document_assembler = DocumentAssembler() \
            .setInputCol('rawContent') \
            .setOutputCol('document')

        tokenizer = Tokenizer() \
            .setInputCols(['document']) \
            .setOutputCol('token')

        #RoBertaForSequenceClassification.pretrained("twitter_roberta_base_sentiment_cardiffnlp", "en")
        sequenceClassifier = DistilBertForSequenceClassification.pretrained("sentiment_twitter160000_3_zhaohui", "en")\
            .setInputCols(["document", 'token']) \
            .setOutputCol("class")

        self.nlp_pipeline = Pipeline(stages=[
            document_assembler,
            tokenizer,
            sequenceClassifier
        ])

        self.model = self.nlp_pipeline.fit(self.train_data)

    def save_model(self):
        # save model in the same code directory
        self.model.save(self.model_path)

def main():
    if len(sys.argv)<2:
        return
    base_directory = sys.argv[1]  + datetime.now().strftime("%Y-%m-%d")
    test_data = DataProcess(base_directory)
    test_data.predict_context_sentiment()
    test_data.labeled_data.show(5)
    test_data.save_data("test_data")
    # sub_directory = "tesla battery since2024-04-04 until2024-04-05_sample"
    #file_name = "tesla battery since2024-04-04 until2024-04-05_sample.json"  # don't include file type!
    #train_data = DataProcess(base_directory)
    #model = TrainModel(train_data)
    #model.fit_pretrained_model()
    #model.save_model()


if __name__ == "__main__":
    main()
