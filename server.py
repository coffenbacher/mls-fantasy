import os
from flask import Flask
from sync import main
from rq import Queue
from redis import Redis, Connection
import redis
from jobs import *
from players.sync import sync_players

app = Flask(__name__)

@app.route("/sync/")
def trigger_sync():
    q = Queue(connection=redis.from_url(os.getenv('REDISCLOUD_URL')))  # no args implies the default queue
    q.enqueue(sync_players)
    return '1'

@app.route("/sync/games/")
def trigger_sync_games():
    q = Queue(connection=redis.from_url(os.getenv('REDISCLOUD_URL')))  # no args implies the default queue
    q.enqueue(sync_new_games)
    return '1'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.debug = os.environ.get("DEBUG")
    app.run(host='0.0.0.0', port=port)