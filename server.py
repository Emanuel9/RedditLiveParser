#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "emanuel.dumitru9@gmail.com"

import logging
import flask
from bson.json_util import dumps
from pymongo import MongoClient
from flask import Flask, request
from flask.views import MethodView
from flask.ext.api import status

class RequestForRedditItems(object):

    def __init__(self, collection, subreddit, from_date, to_date, keyword):
        self.collection = collection
        self.subreddit  = subreddit
        self.from_date  = from_date
        self.to_date    = to_date
        self.keyword    = keyword

    def check_request_params_are_ok(self):
        if self.subreddit is None or self.from_date is None or self.to_date is None:
            return False
        return True

    def create_connection_db(self):
        self.mongo_connection = MongoClient()
        self.db = self.mongo_connection.reddit_data

    def close_connection_db(self):
        self.mongo_connection.close()

    def get_reddit_items(self, from_date, to_date):
        self.create_connection_db()
        if self.keyword is not None:
            data = self.db[self.collection].find({
                "$and" : [
                    {"subreddit" : self.subreddit},
                    {"$and" : [
                        {"created_date" : {"$gte" : from_date}},
                        {"created_date" : {"$lte" : to_date}}
                    ]},
                    {"$or" : [
                        {"title" : {"$regex" : ".*%s.*" % self.keyword}},
                        {"comment_text" : {"$regex" : ".*%s.*" % self.keyword}},
                    ]}
                ]
            }).sort("created_date", -1)
        else:
            data = self.db[self.collection].find({
                "$and" : [
                    {"subreddit" : self.subreddit},
                    {"$and" : [
                        {"created_date" : {"$gte" : from_date}},
                        {"created_date" : {"$lte" : to_date}}
                    ]}
                ]
            }).sort("created_date", -1)
        self.close_connection_db()
        return data


class ProcessRequest(flask.views.MethodView):
    def get(self):
        req = RequestForRedditItems('reddit_items', subreddit=request.args.get('subreddit'), from_date=request.args.get('from'), to_date=request.args.get('to'), keyword=request.args.get('keyword'))
        if req.check_request_params_are_ok() == False:
            return 'HTTP Status 400 - Bad request! Please provide the required params(subreddit, from and to)!', status.HTTP_400_BAD_REQUEST
        response_data = req.get_reddit_items(int(str(req.from_date)), int(str(req.to_date)))
        response_data_json_format = dumps(response_data, indent=4, separators=(',', ': '))

        return response_data_json_format, status.HTTP_200_OK

app = Flask('RedditLiveParser')
app.add_url_rule('/items', view_func=ProcessRequest.as_view('reddit_items_view'))

if __name__ == '__main__':
    logging.basicConfig(filename='log/server.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
