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


# ✅ دالة لجلب الاسم والمنطقة باستخدام data.get()
def get_player_info(player_id):
    cookies = {
        '_ga': 'GA1.1.2123120599.1674510784',
        '_fbp': 'fb.1.1674510785537.363500115',
        '_ga_7JZFJ14B0B': 'GS1.1.1674510784.1.1.1674510789.0.0.0',
        'source': 'mb',
        'region': 'MA',
        'language': 'ar',
        '_ga_TVZ1LG7BEB': 'GS1.1.1674930050.3.1.1674930171.0.0.0',
        'datadome': '6h5F5cx_GpbuNtAkftMpDjsbLcL3op_5W5Z-npxeT_qcEe_7pvil2EuJ6l~JlYDxEALeyvKTz3~LyC1opQgdP~7~UDJ0jYcP5p20IQlT3aBEIKDYLH~cqdfXnnR6FAL0',
        'session_key': 'efwfzwesi9ui8drux4pmqix4cosane0y',
    }

    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://shop2game.com',
        'Referer': 'https://shop2game.com/app/100067/idlogin',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Redmi Note 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
        'accept': 'application/json',
        'content-type': 'application/json',
        'x-datadome-clientid': '6h5F5cx_GpbuNtAkftMpDjsbLcL3op_5W5Z-npxeT_qcEe_7pvil2EuJ6l~JlYDxEALeyvKTz3~LyC1opQgdP~7~UDJ0jYcP5p20IQlT3aBEIKDYLH~cqdfXnnR6FAL0',
    }

    json_data = {
        'app_id': 100067,
        'login_id': f'{player_id}',
        'app_server_id': 0,
    }

    try:
        res = requests.post('https://shop2game.com/api/auth/player_id_login', cookies=cookies, headers=headers, json=json_data)
        if res.status_code == 200:
            data = res.json()
            return {
                "nickname": data.get("nickname", "❌ غير متوفر"),
                "region": data.get("region", "❌ غير معروف")
            }
    except:
        pass

    return {
        "nickname": "❌ فشل في جلب الاسم",
        "region": "❌ فشل في جلب المنطقة"
    }


# ✅ دالة فحص الحظر من Garena
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
        player_info = get_player_info(player_id)

        if response.status_code == 200:
            data = response.json().get("data", {})
            is_banned = data.get("is_banned", 0)
            period = data.get("period", 0)

            result = {
                "✅ status": "تم فحص الحساب بنجاح",
                "🆔 UID": player_id,
                "🏷️ Nickname": player_info["nickname"],
                "🌍 Region": player_info["region"],
                "🔒 Account": "🚫 BANNED" if is_banned else "✅ NOT BANNED",
                "⏳ Duration": f"{period} days" if is_banned else "No ban",
                "📊 Banned?": bool(is_banned),
                "💎 Powered by": "@Mohd1_aaqib",
                "📡 Channel": "https://t.me/Mohd1like"
            }

            return Response(json.dumps(result, indent=4, ensure_ascii=False), mimetype="application/json")

        else:
            return Response(json.dumps({
                "❌ error": "Failed to fetch ban status from Garena server",
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
        }, indent=4), mimetype="application/json")

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