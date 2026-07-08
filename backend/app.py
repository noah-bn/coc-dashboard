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
HEADERS = {"Authorization": f"Bearer {COC_API_TOKEN}"}


@app.get("/api/currentwar")
def current_war():
    response = requests.get(
        f"https://api.clashofclans.com/v1/clans/%23{CLAN_TAG}/currentwar",
        headers=HEADERS,
    )
    data = response.json()

    if data["state"] != "notInWar":
        # TODO: shape inWar/preparation/warEnded into the same friendly
        # format get_cwl_war_data produces, instead of raw passthrough.
        return data

    cwl_response = requests.get(
        f"https://api.clashofclans.com/v1/clans/%23{CLAN_TAG}/currentwar/leaguegroup",
        headers=HEADERS,
    )
    cwl_data = cwl_response.json()

    if cwl_data.get("state") not in ("inWar", "preparation"):
        return {"state": "notInWar"}

    our_rounds = format_cwl_league_data(cwl_data["rounds"])
    current_round = next((w for w in our_rounds if w["state"] != "warEnded"), None)

    return {
        "leagueState": cwl_data["state"],
        "leagueSeason": cwl_data["season"],
        "currentRound": current_round,
        "rounds": our_rounds,
    }


def format_cwl_league_data(rounds):
    # Check every round in the league group and return formatted war data
    # for the wars that involve our clan (skipping unpaired "#0" slots).
    our_tag = f"#{CLAN_TAG}"
    formatted_cwl = []

    for war_round in rounds:
        for tag in war_round["warTags"]:
            if tag == "#0":
                continue  # round not paired yet - later added "war not started" to display

            encoded_tag = tag.replace("#", "%23")
            response = requests.get(
                f"https://api.clashofclans.com/v1/clanwarleagues/wars/{encoded_tag}",
                headers=HEADERS,
            )
            data = response.json()
            if data["clan"]["tag"] == our_tag or data["opponent"]["tag"] == our_tag:
                formatted_cwl.append(get_cwl_war_data(data))
                break  # only one war per round can involve our clan

    return formatted_cwl


def get_cwl_war_data(data):
    our_tag = f"#{CLAN_TAG}"
    us, opponent = (
        (data["clan"], data["opponent"])
        if data["clan"]["tag"] == our_tag
        else (data["opponent"], data["clan"])
    )

    opponent_names_by_tag = {m["tag"]: m["name"] for m in opponent["members"]}
    opponent_position_by_tag = {m["tag"]: m["mapPosition"] for m in opponent["members"]}

    members = []
    for member in us["members"]:
        attacks = [
            {
                "defenderName": opponent_names_by_tag.get(a["defenderTag"], "Unknown"),
                "defenderMapPosition": opponent_position_by_tag.get(
                    a["defenderTag"], "Unknown"
                ),
                "stars": a["stars"],
                "destructionPercentage": a["destructionPercentage"],
            }
            for a in member.get("attacks", [])
        ]
        members.append(
            {
                "name": member["name"],
                "townhallLevel": member["townhallLevel"],
                "mapPosition": member["mapPosition"],
                "attacks": attacks,
            }
        )

    return {
        "state": data["state"],
        "clanName": us["name"],
        "startTime": data["startTime"],
        "endTime": data["endTime"],
        "preparationStartTime": (
            data["preparationStartTime"] if data["state"] == "preparation" else None
        ),
        "attacksCompleted": us["attacks"],
        "totalAttacks": data["teamSize"],  # CWL is always 1 attack per member
        "starsGained": us["stars"],
        "totalDestructionPercentage": us["destructionPercentage"],
        "members": members,
    }


if __name__ == "__main__":
    app.run(debug=False, port=5000)
