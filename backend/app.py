import os

import requests
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

COC_API_TOKEN = os.environ["COC_API_TOKEN"]
CLAN_TAG = os.environ["CLAN_TAG"]


@app.get("/api/currentwar")
def current_war():
    response = requests.get(
        f"https://api.clashofclans.com/v1/clans/%23{CLAN_TAG}/currentwar",
        headers={"Authorization": f"Bearer {COC_API_TOKEN}"},
    )
    return response.json()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
