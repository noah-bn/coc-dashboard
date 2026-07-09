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
        regular_war = get_regular_war_data(data)
        return {
            "warType": "regular",
            "currentRound": regular_war,
            "rounds": [regular_war],
        }

    cwl_response = requests.get(
        f"https://api.clashofclans.com/v1/clans/%23{CLAN_TAG}/currentwar/leaguegroup",
        headers=HEADERS,
    )
    cwl_data = cwl_response.json()

    if cwl_data.get("state") not in ("inWar", "preparation"):
        return {"state": "notInWar"}

    our_rounds = format_cwl_league_data(cwl_data["rounds"])
    current_round = next(
        (w for w in our_rounds if w["state"] in ("inWar", "preparation")), None
    )

    return {
        "warType": "cwl",
        "leagueState": cwl_data["state"],
        "leagueSeason": cwl_data["season"],
        "currentRound": current_round,
        "rounds": our_rounds,
    }


def format_cwl_league_data(rounds):
    # Every round gets an entry, in order - rounds not yet paired/reachable
    # become a {"state": "notStarted"} placeholder instead of being skipped,
    # so the frontend can render all 7 round tabs regardless of how far the
    # league has progressed.
    our_tag = f"#{CLAN_TAG}"
    formatted_cwl = []

    for war_round in rounds:
        round_data = None
        for tag in war_round["warTags"]:
            if tag == "#0":
                continue  # slot not paired yet

            encoded_tag = tag.replace("#", "%23")
            response = requests.get(
                f"https://api.clashofclans.com/v1/clanwarleagues/wars/{encoded_tag}",
                headers=HEADERS,
            )
            if response.status_code != 200:
                continue  # round exists but isn't fetchable yet
            data = response.json()
            if data["clan"]["tag"] == our_tag or data["opponent"]["tag"] == our_tag:
                round_data = get_cwl_war_data(data)
                break  # only one war per round can involve our clan

        formatted_cwl.append(round_data or {"state": "notStarted"})

    return formatted_cwl


def shape_war_members(us_members, opponent_members):
    # Shared by CWL and regular wars - both use the same member/attack shape,
    # they only differ in how many attacks a member is allowed.
    opponent_names_by_tag = {m["tag"]: m["name"] for m in opponent_members}
    opponent_position_by_tag = {m["tag"]: m["mapPosition"] for m in opponent_members}

    members = []
    for member in us_members:
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
    return members


def shape_war_data(data, war_type, attacks_per_member):
    our_tag = f"#{CLAN_TAG}"
    us, opponent = (
        (data["clan"], data["opponent"])
        if data["clan"]["tag"] == our_tag
        else (data["opponent"], data["clan"])
    )

    return {
        "warType": war_type,
        "state": data["state"],
        "clanName": us["name"],
        "startTime": data["startTime"],
        "endTime": data["endTime"],
        "preparationStartTime": (
            data["preparationStartTime"] if data["state"] == "preparation" else None
        ),
        "attacksPerMember": attacks_per_member,
        "attacksCompleted": us["attacks"],
        "totalAttacks": data["teamSize"] * attacks_per_member,
        "starsGained": us["stars"],
        "totalDestructionPercentage": us["destructionPercentage"],
        "members": shape_war_members(us["members"], opponent["members"]),
        "opponent": {
            "name": opponent["name"],
            "attacksCompleted": opponent["attacks"],
            "starsGained": opponent["stars"],
            "totalDestructionPercentage": opponent["destructionPercentage"],
        },
    }


def get_cwl_war_data(data):
    return shape_war_data(data, war_type="cwl", attacks_per_member=1)


def get_regular_war_data(data):
    return shape_war_data(
        data, war_type="regular", attacks_per_member=data["attacksPerMember"]
    )


if __name__ == "__main__":
    app.run(debug=False, port=5000)
