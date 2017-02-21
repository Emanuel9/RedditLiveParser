#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "emanuel.dumitru9@gmail.com"


import logging
import flask
from flask import Flask, request
from flask.views import MethodView

class ProcessRequest(flask.views.MethodView):
    def get(self):
        subreddit = request.args.get('subreddit')
        from_date = request.args.get('from')
        to_date   = request.args.get('to')
        keyword   = request.args.get('keyword')

        logging.info("%s %s %s %s" % (subreddit, from_date, to_date, keyword))

        return "Created endpoint"

if __name__ == '__main__':
    logging.basicConfig(filename='log/server.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    app = Flask('RedditLiveParser')
    app.add_url_rule('/items', view_func=ProcessRequest.as_view('RedditLiveParserServer'))
    app.debug = True
    app.run(host='0.0.0.0', port=80)
