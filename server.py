import os
from flask import Flask
from sync import main

app = Flask(__name__)

@app.route("/sync/")
def trigger_sync():
    main()
    return '1'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.debug = os.environ.get("DEBUG")
    app.run(host='0.0.0.0', port=port)