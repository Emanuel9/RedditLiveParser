# RedditLiveParser

RedditLiveParser is a small system that parses reddit submissions and comments using
praw API, grabs them, formats them and then update from hour to hour a
mongo db : reddit_items. It expose reddit data with filtering capabilities through an HTTP API.

Ex:

http://localhost:5000/items?subreddit=news&from=1488374315%20&to=1488482143&keyword=of

Optimization could be developed when we have a big period to fetch data, to split 
the process that fetch data and store in db in many processes. 

Ex: current_date - start_point_date = 6months.
Fetch 6 chunks of 1month.

Everything will be logged in files from log directory:
- reddit-parser.log for reddit-parser.py, script that parse reddit data and save to mongo each hour
- server.log for server.py, flask server that will listen for requests and will respond
with json responses containing reddit submissions and comments based on the subreddit
, time frames and optionally keyword given through request params.
- test.log for test.py, script used for testing functionallity of the system

There will be two databases: reddit_items and temporarly reddit_items_test for unittesting

Config files will be read from config directory from files:
- config.json or config-test.json for testing

python test.py for tests ... passed 7 out of 7
python reddit_parser.py
python server.py

Dockerfile, requirements.txt and docker-compose.yml for Dockerfile

docker-compose build
docker-compose up






