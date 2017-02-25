#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "emanuel.dumitru9@gmail.com"

import logging
import json
import praw
import time
import datetime
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
    def __init__(self):
        self.get_config_data()
        self.subreddits = self.input["subreddits"]
        self.client_id = self.input["client_id"]
        self.client_secret = self.input["client_secret"]
        self.password = self.input["password"]
        self.username = self.input["username"]
        self.user_agent = self.input["user_agent"]
        self.starting_point_date = self.input["starting_point_date"]
        self.reddit_API = praw.Reddit(client_id=self.client_id, client_secret=self.client_secret, password=self.password, username=self.username, user_agent=self.user_agent)

    def get_config_data(self):
        with open('config.json') as config_file:
            self.input = json.load(config_file)

    def create_connection_db(self):
        self.mongo_connection = MongoClient()
        self.db = self.mongo_connection.reddit_data

    def close_connection_db(self):
        self.mongo_connection.close()

    def create_mongo_collection_and_index(self):
        self.create_connection_db()
        if "reddit-items" not in self.db.collection_names():
            self.db.reddit_items.create_index([("_id", ASCENDING), ("created_date", DESCENDING), ("subreddit", ASCENDING)], name="reddit_items_index", unique=True, dropDups=1)
        self.close_connection_db()

    def get_submissions_and_comments(self):
        try:
            start_point_date = datetime.datetime.strptime(self.starting_point_date, "%Y-%m-%d %H:%M:%S")
            start_unix_time = time.mktime(start_point_date.timetuple())

            reddit = self.reddit_API
            for subreddit_string in self.subreddits:
                subreddit = reddit.subreddit(subreddit_string)
                for submission in subreddit.submissions(start=start_unix_time, end=None):
                    self.db.reddit_items.save(RedditItem(submission.id, submission.title, None, subreddit_string, submission.created).item)
                    for comment in submission.comments:
                        self.db.reddit_items.save(RedditItem(comment.id, None, comment.body, subreddit_string, comment.created).item)

            logging.info("Succesfully updated reddit data from %s ... " % start_unix_time)

        except Exception as ex:
            logging.error("Exception ocurred, please find out the exception message : %s" % ex.message)


if __name__ == '__main__':
    logging.basicConfig(filename='log/reddit-parser.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    parser = RedditParser()
    parser.create_mongo_collection_and_index()

    while True:
        parser.create_connection_db()
        parser.get_submissions_and_comments()
        parser.close_connection_db()
        time.sleep(20 * 60)




