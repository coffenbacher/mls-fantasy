import os
from flask import Flask
import redis
from rq import Queue, Connection

from jobs import *
from players.sync import sync_players

app = Flask(__name__)

@app.route("/sync/")
def trigger_sync():
    with Connection(redis.from_url(os.getenv('REDISCLOUD_URL'))) as conn:
        q = Queue(connection=conn)  # no args implies the default queue
        q.enqueue(sync_players)
    return '1'

@app.route("/sync/games/")
def trigger_sync_games():
    with Connection(redis.from_url(os.getenv('REDISCLOUD_URL'))) as conn:
        q = Queue(connection=conn)  # no args implies the default queue
        q.enqueue(sync_new_games, timeout=3600)
    return '1'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.debug = os.environ.get("DEBUG")
    app.run(host='0.0.0.0', port=port)