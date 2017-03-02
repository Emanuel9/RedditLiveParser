FROM python:2.7.10
FROM mongo:3.0.2
ADD . /redditLiveParser
WORKDIR /redditLiveParser
RUN pip install -r requirements.txt
CMD ["python", "reddit_parser.py"]
CMD ["python", "server.py"]
