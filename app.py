from flask import Flask
from flask import request
from celery import Celery
from tinydb import TinyDB, Query
import uuid
import copy
import json
import operator

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)

# creating celery app
# celery would be used to handle requests asynchronous
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)

# creating database, tinyDB for now
db = TinyDB('tweets.json')
Tweets = Query()

# symbol to operator
sy_to_op = {
    '==': operator.eq,
    '<': operator.lt,
    '>': operator.gt
}

with open('query_action.json') as fp:
    qa_dict = json.load(fp)  # query_action dict

@celery.task(name="tasks.add_tweet_to_db_and_process")
def add_tweet_to_db_and_process(req_json):
    username = req_json['user']
    user_tweets = db.search(Tweets.user == username) # tweets by particular user
    # tweets sorted by count
    user_tweets_sorted = sorted(
        user_tweets, key=lambda k: k.get('count', 0), reverse=True)
    count = user_tweets_sorted[0].get('count', 0)
    req_json.update({'count': count+1})
    print(req_json)
    db.insert(req_json)
    print("---- TWEET INSERTED IN DB ----")
    # tweet inserted in db with count, now checking for queries
    process_tweet.delay(req_json)


@celery.task(name="tasks.process_tweet")
def process_tweet(tweet):
    for query in qa_dict.values():
        param = query[0] # query on which attribute
        tweet_param_val = tweet.get(param, '') # value of that attribute in tweet
        operation = sy_to_op[query[1]]
        if tweet_param_val:
            if operation(tweet_param_val, query[2]):
                print(f'{query} condition fulfilled')
    print("---- TWEET PROCESSED ----")


@app.route("/", methods=['GET', 'POST'])
def tweet():
    if request.method == 'POST':
        print(request.json)
        uid = str(uuid.uuid4())[:8]
        request.json.update({'id': uid})
        add_tweet_to_db_and_process.delay(request.json)

    return uid, 201


if __name__ == "__main__":
    app.run(debug=True) # flask app
