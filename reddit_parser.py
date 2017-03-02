#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "emanuel.dumitru9@gmail.com"

import logging
import json
import praw
import time
import datetime
from datetime import timedelta
from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING

class RedditItem(object):
    def __init__(self, id, title, comment_text, subreddit, created_date):
        self._item = {}
        self._item["_id"] = id
        if title is not None:
            self._item["title"] = title
        elif comment_text is not None:
            self._item["comment_text"] = comment_text
        self._item["subreddit"] = subreddit
        self._item["created_date"] = created_date

    @property
    def item(self):
        return self._item

class RedditParser(object):
    def __init__(self, config_data_name, logfile):
        self.set_config_data(config_data_name)
        self.subreddits = self.input["subreddits"]
        self.client_id = self.input["client_id"]
        self.client_secret = self.input["client_secret"]
        self.password = self.input["password"]
        self.username = self.input["username"]
        self.user_agent = self.input["user_agent"]
        self.starting_point_date = self.input["starting_point_date"]
        self.reddit_API = praw.Reddit(client_id=self.client_id, client_secret=self.client_secret, password=self.password, username=self.username, user_agent=self.user_agent)
        self.logfile = logfile

    def set_config_data(self, config_data_name):
        with open(config_data_name) as config_file:
            self.input = json.load(config_file)

    def create_connection_db(self):
        self.mongo_connection = MongoClient()
        self.db = self.mongo_connection.reddit_data

    def close_connection_db(self):
        self.mongo_connection.close()

    def create_mongo_collection_and_index(self, collection_name):
        self.create_connection_db()
        if collection_name not in self.db.collection_names():
            self.db[collection_name].create_index([("_id", ASCENDING), ("created_date", DESCENDING), ("subreddit", ASCENDING)], name="reddit_items_index", unique=True, dropDups=1)
        self.close_connection_db()

    def get_submissions_and_comments(self, collection, testing_purpose):
        try:
            start_point_date = datetime.datetime.strptime(self.starting_point_date, "%Y-%m-%d %H:%M:%S")
            start_unix_time = time.mktime(start_point_date.timetuple())

            if testing_purpose == True:
                end_point_date = start_point_date + timedelta(hours=1)
                end_unix_time = time.mktime(end_point_date.timetuple())
            else:
                end_unix_time = None

            reddit = self.reddit_API
            submissions = []
            comments = []
            for subreddit_string in self.subreddits:
                logging.info("Starting to fetch reddit data for subreddit %s from %s ... " % (subreddit_string, start_unix_time))
                subreddit = reddit.subreddit(subreddit_string)
                subreddit_submissions = [submission for submission in subreddit.submissions(start=start_unix_time, end=end_unix_time)]
                subreddit_comments = [comment for submission in subreddit_submissions for comment in submission.comments]

                self.create_connection_db()
                for submission in subreddit_submissions:
                    self.db[collection].save(RedditItem(submission.id, submission.title, None, subreddit_string, submission.created_utc).item)

                for comment in subreddit_comments:
                    self.db[collection].save(RedditItem(comment.id, None, comment.body, subreddit_string, comment.created_utc).item)
                self.close_connection_db()
                logging.info("Successfully update reddit data for subreddit %s from %s ... " % (subreddit_string, start_unix_time))

                submissions += subreddit_submissions
                comments    += subreddit_comments


            logging.info("Succesfully updated reddit data from %s ... " % start_unix_time)
            return submissions + comments

        except Exception as ex:
            logging.error("Exception ocurred, please find out the exception message : %s" % ex.message)


if __name__ == '__main__':
    parser = RedditParser('config/config.json', 'log/reddit-parser.log')
    logging.basicConfig(filename=parser.logfile, filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    parser.create_mongo_collection_and_index('reddit_items')

    while True:
        parser.get_submissions_and_comments('reddit_items', testing_purpose=False)
        time.sleep(60 * 60)




