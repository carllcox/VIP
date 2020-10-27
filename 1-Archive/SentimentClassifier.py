import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import BernoulliNB


class SentimentClassifier:
    def __init__(self):
        self.classifier = BernoulliNB()
        self.trainDocuments = []
        self.trainLabels = []
        self.count_vectorizer = CountVectorizer(binary="true")

    def aggregateTrainingData(self, datafiles=None):
        """
        Aggregates labeled training data passed in from datafiles
        """
        # with open("classifierData/imdb_labelled.txt", "r") as text_file:
        # 	lines = text_file.read().split("\n")

        # with open("classifierData/amazon_cells_labelled.txt", "r") as text_file:
        #     lines = text_file.read().split("\n")

        # with open("classifierData/yelp_labelled.txt", "r") as text_file:
        #     lines = text_file.read().split("\n")

        with open("classifierData/masterdata_labelled.txt", "r") as text_file:
            lines = text_file.read().split("\n")

        newLines = [line.split("\t") for line in lines if len(
            line.split("t")) == 2 and line.split("\t")[1] != ""]

        # Split data into Train Features & Train Labels:
        self.trainDocuments = [line[0] for line in newLines]

        self.trainLabels = [int(line[1]) for line in newLines]

        self.vectorizeTrainingData()

    def vectorizeTrainingData(self):
        # Convert the training set to a matrix of token counts:
        self.trainDocuments = self.count_vectorizer.fit_transform(self.trainDocuments)

    def trainClassifier(self):
        """
        Fit the classifier to the training data
        """
        # if not self.trainDocuments:
        #     print("No training data!")

        self.classifier = self.classifier.fit(
            self.trainDocuments, self.trainLabels)

    def predictionOutput(self, sentence):
        """
        This function outputs the sentiment analysis label (Positive or Negative) for a given sentence
        """
        prediction = self.classifier.predict(
              self.count_vectorizer.transform([sentence]))
        if prediction[0] == 1:
            print("This is a Positive Sentiment")
        elif prediction[0] == 0:
            print("This is a Negative Sentiment")