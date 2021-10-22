## event condition action server based on flask + celery

#### install dependencies via following command
pip install -r requirements.txt

#### run flask app in one terminal window
python3 app.py

#### run celery app in another terminal window
celery -A app.celery worker

#### use driver file to post the tweets
#### last argument is number of tweets that you want to post
python3 test.py 1