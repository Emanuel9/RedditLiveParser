#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "emanuel.dumitru9@gmail.com"

import json
import pymongo
import unittest
import datetime
import time
from datetime import timedelta
from server import app, RequestForRedditItems
from reddit_parser import RedditParser

class RedditLiveParserTestCase(unittest.TestCase):

    #Flask server tests
    def test_flask_bad_request(self):
        tester = app.test_client()
        response = tester.get('/items?subredit=test', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_flask_correct_request_without_keyword(self):
        tester = app.test_client()
        response = tester.get('/items?subreddit=test&from=1488052247&to=1488049923', content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_flask_correct_request_with_keyword(self):
        tester = app.test_client()
        response = tester.get('/items?subreddit=test&from=1488052247&to=1488049923&keyword=was', content_type='application/json')
        self.assertEqual(response.status_code, 200)

    #Reddit parser tests
    def test_reddit_parser_retrieved_config_file(self):
        with open('config/config.json') as config_file:
            cfg_file = json.load(config_file)

        rp = RedditParser('config/config.json', 'log/test.log')
        self.assertEqual(cfg_file, rp.input)

    def test_reddit_parser_mongo_connection(self):
        rp = RedditParser('config/config.json', 'log/test.log')
        connection_established = True
        try:
            rp.create_connection_db()
            rp.mongo_connection.server_info()
            rp.close_connection_db()
        except pymongo.errors.ServerSelectionTimeoutError:
            connection_established = False

        self.assertEqual(connection_established, True)

    def test_reddit_parser_mongo_collection(self):
        rp = RedditParser('config/config.json', 'log/test.log')
        rp.create_mongo_collection_and_index('reddit_items_test')
        collection_exists = 'reddit_items_test' in rp.db.collection_names()
        self.assertEqual(collection_exists, True)
        rp.db['reddit_items_test'].drop()

    def test_reddit_parser_retrieve_reddit_data(self):
        rp = RedditParser('config/config-test.json', 'log/test.log')
        start_point_date = datetime.datetime.strptime(rp.starting_point_date, "%Y-%m-%d %H:%M:%S")
        start_unix_time = time.mktime(start_point_date.timetuple())
        end_point_date = start_point_date + timedelta(hours=1)
        end_unix_time = time.mktime(end_point_date.timetuple())
        server = RequestForRedditItems(collection='reddit_items_test', subreddit=rp.subreddits[0], from_date=int(start_unix_time), to_date=int(end_unix_time), keyword=None)


        rp.create_mongo_collection_and_index('reddit_items_test')
        reddit_parser_data = rp.get_submissions_and_comments('reddit_items_test', testing_purpose=True)

        data = server.get_reddit_items(int(start_unix_time), int(end_unix_time))
        self.assertEqual(len(reddit_parser_data), data.count())
        rp.db['reddit_items_test'].drop()


if __name__ == '__main__':
    unittest.main()