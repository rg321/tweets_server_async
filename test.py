import requests
import json
import random
import sys
from time import sleep

url = "http://127.0.0.1:5000/"

users = ["Anuj", "Raghav"]
locations = ["Pune", "London"]
payload = json.dumps({
    "user": random.choice(users),
    "tweet": "my first tweet",
    "location": random.choice(locations),
})
headers = {
    'Content-Type': 'application/json'
}

def tweet():
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    assert response.status_code == 201


if __name__ == '__main__':
    n = sys.argv[1]
    for i in range(int(n)):
        print(f'tweet {i}')
        sleep(0.5)
        tweet()
