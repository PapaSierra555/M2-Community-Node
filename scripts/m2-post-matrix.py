#!/usr/bin/env python3
# m2-post-matrix.py — posts a text message to a Matrix room
# Usage: python3 m2-post-matrix.py <token> <base_url> <room_id> <message>
# Deploy to: /usr/local/bin/m2-post-matrix.py

import sys
import json
import ssl
import time
import urllib.request
import urllib.parse

def main():
    if len(sys.argv) != 5:
        print("Usage: m2-post-matrix.py <token> <base_url> <room_id> <message>")
        sys.exit(1)

    token, base_url, room_id, msg = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    txn_id = str(int(time.time() * 1000))
    url = "{}/{}{}{}".format(
        base_url,
        "_matrix/client/v3/rooms/",
        urllib.parse.quote(room_id, safe=""),
        "/send/m.room.message/" + txn_id
    )
    body = json.dumps({"msgtype": "m.text", "body": msg}).encode()
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; m2-status-bot/1.0)"
    }
    req = urllib.request.Request(url, data=body, method="PUT", headers=headers)
    ctx = ssl.create_default_context()
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        print(json.loads(resp.read()))
    except urllib.error.HTTPError as e:
        print("HTTP {}: {}".format(e.code, e.read()[:300]))
        sys.exit(1)
    except Exception as e:
        print("Error: {}".format(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
