"""Quick standalone test for the CWL response-shaping logic in app.py.

Run with: python test_cwl.py
No pytest/network required - uses the sample war JSON pasted from a real
API response, and mocks requests.get for the format_cwl_league_data pass.
"""

import json
import os
from unittest.mock import patch

os.environ.setdefault("COC_API_TOKEN", "test-token")
os.environ.setdefault("CLAN_TAG", "2QYCRRVU8")  # PropellerPerps, matches SAMPLE_WAR below

from app import format_cwl_league_data, get_cwl_war_data  # noqa: E402

SAMPLE_WAR = json.loads(r"""
{
  "state": "warEnded",
  "teamSize": 15,
  "preparationStartTime": "20260701T204555.000Z",
  "startTime": "20260702T204518.000Z",
  "endTime": "20260703T204518.000Z",
  "clan": {
    "tag": "#2QYCRRVU8",
    "name": "PropellerPerps",
    "badgeUrls": {
      "small": "https://api-assets.clashofclans.com/badges/70/sVn51Q3Rm2EuexQYI0Wau1lydeFRgeNJvGcTcEvp1qI.png",
      "large": "https://api-assets.clashofclans.com/badges/512/sVn51Q3Rm2EuexQYI0Wau1lydeFRgeNJvGcTcEvp1qI.png",
      "medium": "https://api-assets.clashofclans.com/badges/200/sVn51Q3Rm2EuexQYI0Wau1lydeFRgeNJvGcTcEvp1qI.png"
    },
    "clanLevel": 11,
    "attacks": 13,
    "stars": 22,
    "destructionPercentage": 58.86666666666667,
    "members": [
      {"tag": "#QQLVV0LP", "name": "Lalo", "townhallLevel": 15, "mapPosition": 3,
       "attacks": [{"attackerTag": "#QQLVV0LP", "defenderTag": "#YGJY0QLRR", "stars": 2, "destructionPercentage": 74, "order": 13, "duration": 144}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#YGJY0QLRR", "defenderTag": "#QQLVV0LP", "stars": 3, "destructionPercentage": 100, "order": 18, "duration": 81}},
      {"tag": "#GRQQV22R", "name": "Ironghost6954", "townhallLevel": 15, "mapPosition": 4,
       "attacks": [{"attackerTag": "#GRQQV22R", "defenderTag": "#LCL2CC9GR", "stars": 2, "destructionPercentage": 52, "order": 21, "duration": 125}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#LCL2CC9GR", "defenderTag": "#GRQQV22R", "stars": 3, "destructionPercentage": 100, "order": 17, "duration": 120}},
      {"tag": "#229R2R2JV", "name": "Ninja Sloth", "townhallLevel": 14, "mapPosition": 6,
       "attacks": [{"attackerTag": "#229R2R2JV", "defenderTag": "#LUGV2CQG8", "stars": 2, "destructionPercentage": 77, "order": 6, "duration": 137}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#LUGV2CQG8", "defenderTag": "#229R2R2JV", "stars": 3, "destructionPercentage": 100, "order": 16, "duration": 100}},
      {"tag": "#YJP8P9P8", "name": "Couffe", "townhallLevel": 16, "mapPosition": 2,
       "attacks": [{"attackerTag": "#YJP8P9P8", "defenderTag": "#LJQVQ2LGG", "stars": 2, "destructionPercentage": 94, "order": 22, "duration": 180}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#LJQVQ2LGG", "defenderTag": "#YJP8P9P8", "stars": 3, "destructionPercentage": 100, "order": 20, "duration": 158}},
      {"tag": "#LGPYUR2UJ", "name": "LogieBogie2", "townhallLevel": 10, "mapPosition": 20,
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#G2PVL99CJ", "defenderTag": "#LGPYUR2UJ", "stars": 3, "destructionPercentage": 100, "order": 9, "duration": 62}},
      {"tag": "#JGR0C2J9", "name": "blubirdfreshies", "townhallLevel": 12, "mapPosition": 17,
       "attacks": [{"attackerTag": "#JGR0C2J9", "defenderTag": "#GPUQY2QRR", "stars": 1, "destructionPercentage": 42, "order": 5, "duration": 92}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#G8GCGRJ22", "defenderTag": "#JGR0C2J9", "stars": 3, "destructionPercentage": 100, "order": 10, "duration": 65}},
      {"tag": "#8J88LU22R", "name": "Dexterity", "townhallLevel": 14, "mapPosition": 7,
       "attacks": [{"attackerTag": "#8J88LU22R", "defenderTag": "#L88Q2GPRR", "stars": 3, "destructionPercentage": 100, "order": 25, "duration": 102}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#L88Q2GPRR", "defenderTag": "#8J88LU22R", "stars": 3, "destructionPercentage": 100, "order": 4, "duration": 136}},
      {"tag": "#R28LQ8R99", "name": "parkdaddy", "townhallLevel": 10, "mapPosition": 24,
       "attacks": [{"attackerTag": "#R28LQ8R99", "defenderTag": "#G2PVL99CJ", "stars": 0, "destructionPercentage": 44, "order": 12, "duration": 73}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#GPVY80JVG", "defenderTag": "#R28LQ8R99", "stars": 3, "destructionPercentage": 100, "order": 7, "duration": 50}},
      {"tag": "#28GVCRJ0C", "name": "LogieBogie", "townhallLevel": 16, "mapPosition": 1,
       "attacks": [{"attackerTag": "#28GVCRJ0C", "defenderTag": "#Y00L2PQ9", "stars": 2, "destructionPercentage": 77, "order": 15, "duration": 180}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#Y00L2PQ9", "defenderTag": "#28GVCRJ0C", "stars": 3, "destructionPercentage": 100, "order": 2, "duration": 151}},
      {"tag": "#2CVG902RC", "name": "Jexor", "townhallLevel": 15, "mapPosition": 5,
       "attacks": [{"attackerTag": "#2CVG902RC", "defenderTag": "#LPVVUYJGP", "stars": 2, "destructionPercentage": 75, "order": 1, "duration": 142}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#LPVVUYJGP", "defenderTag": "#2CVG902RC", "stars": 3, "destructionPercentage": 100, "order": 19, "duration": 145}},
      {"tag": "#R202VCG20", "name": "wamakak", "townhallLevel": 12, "mapPosition": 15,
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#G2PVPG2UU", "defenderTag": "#R202VCG20", "stars": 3, "destructionPercentage": 100, "order": 11, "duration": 62}},
      {"tag": "#R2GULUYGY", "name": "clanrhat", "townhallLevel": 12, "mapPosition": 13,
       "attacks": [{"attackerTag": "#R2GULUYGY", "defenderTag": "#G8GCGRJ22", "stars": 2, "destructionPercentage": 88, "order": 23, "duration": 165}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#QRQUC0PU0", "defenderTag": "#R2GULUYGY", "stars": 3, "destructionPercentage": 100, "order": 27, "duration": 118}},
      {"tag": "#GCGPYVJ08", "name": "Jewbama", "townhallLevel": 13, "mapPosition": 10,
       "attacks": [{"attackerTag": "#GCGPYVJ08", "defenderTag": "#8LV0L2PP", "stars": 3, "destructionPercentage": 100, "order": 3, "duration": 120}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#8LV0L2PP", "defenderTag": "#GCGPYVJ08", "stars": 3, "destructionPercentage": 100, "order": 28, "duration": 134}},
      {"tag": "#GUQ0CYLVP", "name": "ryguy", "townhallLevel": 10, "mapPosition": 22,
       "attacks": [{"attackerTag": "#GUQ0CYLVP", "defenderTag": "#G8GCGRJ22", "stars": 0, "destructionPercentage": 41, "order": 14, "duration": 90}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#GPUQY2QRR", "defenderTag": "#GUQ0CYLVP", "stars": 3, "destructionPercentage": 100, "order": 8, "duration": 63}},
      {"tag": "#YLPC8PGC9", "name": "JuJu", "townhallLevel": 13, "mapPosition": 9,
       "attacks": [{"attackerTag": "#YLPC8PGC9", "defenderTag": "#L2CUU8RGY", "stars": 1, "destructionPercentage": 60, "order": 26, "duration": 153}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#L2CUU8RGY", "defenderTag": "#YLPC8PGC9", "stars": 3, "destructionPercentage": 100, "order": 24, "duration": 120}}
    ]
  },
  "opponent": {
    "tag": "#2G2VGLC9Y",
    "name": "Element Clan :)",
    "badgeUrls": {
      "small": "https://api-assets.clashofclans.com/badges/70/D9MCNh7OcTrByMkcFsCxFpqm5_52L0OzTTQLhQcYOTs.png",
      "large": "https://api-assets.clashofclans.com/badges/512/D9MCNh7OcTrByMkcFsCxFpqm5_52L0OzTTQLhQcYOTs.png",
      "medium": "https://api-assets.clashofclans.com/badges/200/D9MCNh7OcTrByMkcFsCxFpqm5_52L0OzTTQLhQcYOTs.png"
    },
    "clanLevel": 15,
    "attacks": 15,
    "stars": 45,
    "destructionPercentage": 100.0,
    "members": [
      {"tag": "#YGJY0QLRR", "name": "di Gardien", "townhallLevel": 18, "mapPosition": 4,
       "attacks": [{"attackerTag": "#YGJY0QLRR", "defenderTag": "#QQLVV0LP", "stars": 3, "destructionPercentage": 100, "order": 18, "duration": 81}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#QQLVV0LP", "defenderTag": "#YGJY0QLRR", "stars": 2, "destructionPercentage": 74, "order": 13, "duration": 144}},
      {"tag": "#L88Q2GPRR", "name": "Phönix [501st]", "townhallLevel": 18, "mapPosition": 12,
       "attacks": [{"attackerTag": "#L88Q2GPRR", "defenderTag": "#8J88LU22R", "stars": 3, "destructionPercentage": 100, "order": 4, "duration": 136}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#8J88LU22R", "defenderTag": "#L88Q2GPRR", "stars": 3, "destructionPercentage": 100, "order": 25, "duration": 102}},
      {"tag": "#GPUQY2QRR", "name": "snowkidtv 23.0", "townhallLevel": 14, "mapPosition": 20,
       "attacks": [{"attackerTag": "#GPUQY2QRR", "defenderTag": "#GUQ0CYLVP", "stars": 3, "destructionPercentage": 100, "order": 8, "duration": 63}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#JGR0C2J9", "defenderTag": "#GPUQY2QRR", "stars": 1, "destructionPercentage": 42, "order": 5, "duration": 92}},
      {"tag": "#Y00L2PQ9", "name": "dak", "townhallLevel": 18, "mapPosition": 1,
       "attacks": [{"attackerTag": "#Y00L2PQ9", "defenderTag": "#28GVCRJ0C", "stars": 3, "destructionPercentage": 100, "order": 2, "duration": 151}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#28GVCRJ0C", "defenderTag": "#Y00L2PQ9", "stars": 2, "destructionPercentage": 77, "order": 15, "duration": 180}},
      {"tag": "#LPVVUYJGP", "name": "fabien", "townhallLevel": 17, "mapPosition": 7,
       "attacks": [{"attackerTag": "#LPVVUYJGP", "defenderTag": "#2CVG902RC", "stars": 3, "destructionPercentage": 100, "order": 19, "duration": 145}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#2CVG902RC", "defenderTag": "#LPVVUYJGP", "stars": 2, "destructionPercentage": 75, "order": 1, "duration": 142}},
      {"tag": "#LUGV2CQG8", "name": "mo", "townhallLevel": 16, "mapPosition": 11,
       "attacks": [{"attackerTag": "#LUGV2CQG8", "defenderTag": "#229R2R2JV", "stars": 3, "destructionPercentage": 100, "order": 16, "duration": 100}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#229R2R2JV", "defenderTag": "#LUGV2CQG8", "stars": 2, "destructionPercentage": 77, "order": 6, "duration": 137}},
      {"tag": "#GPVY80JVG", "name": "snowkidtv 24.0", "townhallLevel": 14, "mapPosition": 19,
       "attacks": [{"attackerTag": "#GPVY80JVG", "defenderTag": "#R28LQ8R99", "stars": 3, "destructionPercentage": 100, "order": 7, "duration": 50}],
       "opponentAttacks": 0},
      {"tag": "#QRQUC0PU0", "name": "fz", "townhallLevel": 14, "mapPosition": 16,
       "attacks": [{"attackerTag": "#QRQUC0PU0", "defenderTag": "#R2GULUYGY", "stars": 3, "destructionPercentage": 100, "order": 27, "duration": 118}],
       "opponentAttacks": 0},
      {"tag": "#8LV0L2PP", "name": "geilo", "townhallLevel": 15, "mapPosition": 15,
       "attacks": [{"attackerTag": "#8LV0L2PP", "defenderTag": "#GCGPYVJ08", "stars": 3, "destructionPercentage": 100, "order": 28, "duration": 134}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#GCGPYVJ08", "defenderTag": "#8LV0L2PP", "stars": 3, "destructionPercentage": 100, "order": 3, "duration": 120}},
      {"tag": "#LCL2CC9GR", "name": "mo", "townhallLevel": 18, "mapPosition": 6,
       "attacks": [{"attackerTag": "#LCL2CC9GR", "defenderTag": "#GRQQV22R", "stars": 3, "destructionPercentage": 100, "order": 17, "duration": 120}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#GRQQV22R", "defenderTag": "#LCL2CC9GR", "stars": 2, "destructionPercentage": 52, "order": 21, "duration": 125}},
      {"tag": "#L2CUU8RGY", "name": "Fluffi43", "townhallLevel": 15, "mapPosition": 14,
       "attacks": [{"attackerTag": "#L2CUU8RGY", "defenderTag": "#YLPC8PGC9", "stars": 3, "destructionPercentage": 100, "order": 24, "duration": 120}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#YLPC8PGC9", "defenderTag": "#L2CUU8RGY", "stars": 1, "destructionPercentage": 60, "order": 26, "duration": 153}},
      {"tag": "#G8GCGRJ22", "name": "snowkidtv 21.0", "townhallLevel": 14, "mapPosition": 22,
       "attacks": [{"attackerTag": "#G8GCGRJ22", "defenderTag": "#JGR0C2J9", "stars": 3, "destructionPercentage": 100, "order": 10, "duration": 65}],
       "opponentAttacks": 2,
       "bestOpponentAttack": {"attackerTag": "#R2GULUYGY", "defenderTag": "#G8GCGRJ22", "stars": 2, "destructionPercentage": 88, "order": 23, "duration": 165}},
      {"tag": "#LJQVQ2LGG", "name": "Thomgioh", "townhallLevel": 18, "mapPosition": 2,
       "attacks": [{"attackerTag": "#LJQVQ2LGG", "defenderTag": "#YJP8P9P8", "stars": 3, "destructionPercentage": 100, "order": 20, "duration": 158}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#YJP8P9P8", "defenderTag": "#LJQVQ2LGG", "stars": 2, "destructionPercentage": 94, "order": 22, "duration": 180}},
      {"tag": "#G2PVPG2UU", "name": "snowkidtv 20.0", "townhallLevel": 14, "mapPosition": 21,
       "attacks": [{"attackerTag": "#G2PVPG2UU", "defenderTag": "#R202VCG20", "stars": 3, "destructionPercentage": 100, "order": 11, "duration": 62}],
       "opponentAttacks": 0},
      {"tag": "#G2PVL99CJ", "name": "snowkidtv 22.0", "townhallLevel": 14, "mapPosition": 23,
       "attacks": [{"attackerTag": "#G2PVL99CJ", "defenderTag": "#LGPYUR2UJ", "stars": 3, "destructionPercentage": 100, "order": 9, "duration": 62}],
       "opponentAttacks": 1,
       "bestOpponentAttack": {"attackerTag": "#R28LQ8R99", "defenderTag": "#G2PVL99CJ", "stars": 0, "destructionPercentage": 44, "order": 12, "duration": 73}}
    ]
  },
  "warStartTime": "20260702T204518.000Z"
}
""")


def check(label, actual, expected):
    status = "PASS" if actual == expected else "FAIL"
    print(f"[{status}] {label}: expected {expected!r}, got {actual!r}")
    return actual == expected


def test_get_cwl_war_data():
    print("--- get_cwl_war_data ---")
    result = get_cwl_war_data(SAMPLE_WAR)
    ok = True
    ok &= check("state", result["state"], "warEnded")
    ok &= check("clanName", result["clanName"], "PropellerPerps")
    ok &= check("startTime", result["startTime"], "20260702T204518.000Z")
    ok &= check("endTime", result["endTime"], "20260703T204518.000Z")
    ok &= check("preparationStartTime", result["preparationStartTime"], None)
    ok &= check("attacksCompleted", result["attacksCompleted"], 13)
    ok &= check("totalAttacks", result["totalAttacks"], 15)
    ok &= check("starsGained", result["starsGained"], 22)
    ok &= check(
        "totalDestructionPercentage", result["totalDestructionPercentage"], 58.86666666666667
    )
    ok &= check("member count", len(result["members"]), 15)
    ok &= check("opponent name", result["opponent"]["name"], "Element Clan :)")
    ok &= check("opponent attacksCompleted", result["opponent"]["attacksCompleted"], 15)
    ok &= check("opponent starsGained", result["opponent"]["starsGained"], 45)
    ok &= check(
        "opponent totalDestructionPercentage", result["opponent"]["totalDestructionPercentage"], 100.0
    )

    lalo = next(m for m in result["members"] if m["name"] == "Lalo")
    ok &= check("Lalo townhallLevel", lalo["townhallLevel"], 15)
    ok &= check("Lalo mapPosition", lalo["mapPosition"], 3)
    ok &= check("Lalo attack count", len(lalo["attacks"]), 1)
    ok &= check("Lalo defenderName", lalo["attacks"][0]["defenderName"], "di Gardien")
    ok &= check("Lalo defenderMapPosition", lalo["attacks"][0]["defenderMapPosition"], 4)
    ok &= check("Lalo stars", lalo["attacks"][0]["stars"], 2)
    ok &= check("Lalo destructionPercentage", lalo["attacks"][0]["destructionPercentage"], 74)

    no_attack_member = next(m for m in result["members"] if m["name"] == "LogieBogie2")
    ok &= check("LogieBogie2 attacks (none made)", no_attack_member["attacks"], [])

    return ok


def test_format_cwl_league_data():
    print("--- format_cwl_league_data ---")
    rounds = [
        {"warTags": ["#0", "#0"]},  # not paired yet, must be skipped
        {"warTags": ["#OURWAR", "#SHOULDNOTBEFETCHED"]},
    ]

    def fake_get(url, headers=None):
        if "OURWAR" in url:
            return _FakeResponse(SAMPLE_WAR)
        raise AssertionError(
            f"fetched {url} after already finding our war this round - break didn't work"
        )

    with patch("app.requests.get", side_effect=fake_get):
        result = format_cwl_league_data(rounds)

    ok = True
    ok &= check("rounds found", len(result), 1)
    ok &= check("found round clanName", result[0]["clanName"], "PropellerPerps")
    return ok


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


if __name__ == "__main__":
    results = [test_get_cwl_war_data(), test_format_cwl_league_data()]
    print()
    if all(results):
        print("All checks passed.")
    else:
        print("Some checks FAILED - see above.")
        raise SystemExit(1)
