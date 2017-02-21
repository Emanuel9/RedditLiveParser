#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "emanuel.dumitru9@gmail.com"

import json
import praw
import pprint
from praw.models import Subreddit
from praw.models import Submission
from praw.models import Comment
from praw.models import SubredditHelper





class RedditParser(object):
    def __init__(self):
        self.read_input()
        self.print_subreddits()
        self.reddit_API = praw.Reddit(client_id='bpsMGO-Mbfy9nQ',
                                      client_secret='oUbXmFvn-u-Twgbifcu2XiHU-Vc',
                                      password='Em@nuel9',
                                      username='demi_1994',
                                      user_agent='RedditLiveParser by /u/demi_1994')
        self.get_submissions()

    def read_input(self):
        with open('config.json') as config_file:
            self.subreddits = json.load(config_file)["subreddits"]

    def print_subreddits(self):
        print self.subreddits

    def get_submissions(self):
        reddit = self.reddit_API
        print(reddit.user.me())
        subreddit = reddit.subreddit('python')
        for submission in subreddit.submissions(start=1487698515, end=1487702115, extra_query=None):
            print "Submission: (%s,%s,%s) " % (submission.id, submission.title, submission.created)
            for comment in submission.comments:
                print "\t\tComment : (%s, %s,\n Body:%s \n) " % (comment.id, comment.created, comment.body)

        print 'am terminat!'
if __name__ == '__main__':
    RedditParser()