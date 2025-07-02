from flask import Flask, request, Response
import requests
import json
import os

app = Flask(__name__)

VALID_API_KEYS = {
    "XZA": "active"
}

def validate_api_key(api_key):
    if not api_key:
        return {"❌ error": "API key is missing", "status_code": 401}
    if api_key not in VALID_API_KEYS:
        return {"❌ error": "Invalid API key", "status_code": 401}
    
    status = VALID_API_KEYS[api_key]
    if status == "inactive":
        return {"⚠️ error": "API key is inactive", "status_code": 403}
    if status == "banned":
        return {"🚫 error": "API key is banned", "status_code": 403}
    
    return {"valid": True}

def check_banned(player_id):
    url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K)",
        "Accept": "application/json",
        "referer": "https://ff.garena.com/en/support/",
        "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get("data", {})
            is_banned = data.get("is_banned", 0)
            period = data.get("period", 0)

            result = {
                "✅ status": "تم فحص الحساب بنجاح",
                "🆔 UID": player_id,
                "🔒 Account": "🚫 BANNED" if is_banned else "✅ NOT BANNED",
                "⏳ Duration": f"{period} days" if is_banned else "No ban",
                "📊 Banned?": bool(is_banned),
                "💎 Powered by": "@Mohd1_aaqib",
                "📡 Channel": "https://t.me/Mohd1like"
            }

            return Response(json.dumps(result, indent=4, ensure_ascii=False), mimetype="application/json")
        else:
            return Response(json.dumps({
                "❌ error": "Failed to fetch data from Garena server",
                "status_code": 500
            }, indent=4), mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({
            "💥 exception": str(e),
            "status_code": 500
        }, indent=4), mimetype="application/json")

@app.route("/Xza-check", methods=["GET"])
def xza_check():
    api_key = request.args.get("key", "")
    player_id = request.args.get("uid", "")

    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation, indent=4, ensure_ascii=False), mimetype="application/json")

    if not player_id:
        return Response(json.dumps({
            "⚠️ error": "Player ID (uid) is required!",
            "status_code": 400
        }, indent=4, ensure_ascii=False), mimetype="application/json")

    return check_banned(player_id)

@app.route("/check_key", methods=["GET"])
def check_key():
    api_key = request.args.get("key", "")
    key_validation = validate_api_key(api_key)

    if "error" in key_validation:
        return Response(json.dumps(key_validation, indent=4, ensure_ascii=False), mimetype="application/json")

    return Response(json.dumps({
        "✅ status": "API Key is valid",
        "🔐 Key Status": VALID_API_KEYS.get(api_key, "unknown")
    }, indent=4, ensure_ascii=False), mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))