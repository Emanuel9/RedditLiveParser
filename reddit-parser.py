#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "emanuel.dumitru9@gmail.com"

import json

class RedditParser(object):
    def __init__(self):
        self.read_input()
        self.print_subreddits()

    def read_input(self):
        with open('config.json') as config_file:
            self.subreddits = json.load(config_file)["subreddits"]

    def print_subreddits(self):
        print self.subreddits

if __name__ == '__main__':
    RedditParser()