#!/usr/bin/env python3
"""
Insert Signal unit icon into OTS icons table and assign it to the
Community Node marker, bypassing milsymbol rendering on the web map.

Run on tactical Pi:
  sudo python3 /tmp/set_node_icon.py
"""

import psycopg2

PNG_PATH = "/tmp/signal_unit.png"
MARKER_UID = "1cec9ca6-0b35-415f-9fd6-5aaf43094c79"
ICONSET_UID = "m2-community-node-icons"
ICONSET_NAME = "M2 Community Node"
FILENAME = "signal_unit.png"
GROUP_NAME = "Community Node"
COT_TYPE = "a-f-G-U-C-S-M-N"

conn = psycopg2.connect(dbname="ots", user="ots", password="ME!ZH!%MdtIJ7?Ynar0X", host="127.0.0.1")
cur = conn.cursor()

# Create iconset if not present
cur.execute("SELECT uid FROM iconsets WHERE uid = %s", (ICONSET_UID,))
if not cur.fetchone():
    cur.execute(
        "INSERT INTO iconsets (name, uid, version) VALUES (%s, %s, %s)",
        (ICONSET_NAME, ICONSET_UID, 1)
    )
    print(f"Created iconset: {ICONSET_NAME}")

# Load PNG bytes
with open(PNG_PATH, "rb") as f:
    png_bytes = f.read()

# Clear marker's icon_id first to avoid FK violation on delete
cur.execute("UPDATE markers SET icon_id = NULL WHERE uid = %s", (MARKER_UID,))

# Remove any existing entry for this COT type
cur.execute("DELETE FROM icons WHERE type2525b = %s", (COT_TYPE,))

# Insert icon
cur.execute(
    """INSERT INTO icons (iconset_uid, filename, "groupName", type2525b, "useCnt", bitmap)
       VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
    (ICONSET_UID, FILENAME, GROUP_NAME, COT_TYPE, 0, psycopg2.Binary(png_bytes))
)
icon_id = cur.fetchone()[0]
print(f"Inserted icon id={icon_id}: {FILENAME} -> {COT_TYPE}")

# Assign icon to Community Node marker
cur.execute(
    "UPDATE markers SET icon_id = %s WHERE uid = %s",
    (icon_id, MARKER_UID)
)
rows = cur.rowcount
print(f"Updated {rows} marker row(s) with icon_id={icon_id}")

conn.commit()
cur.close()
conn.close()
print("Done. No restart needed — web map reads icon on next API call.")
