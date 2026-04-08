#!/usr/bin/env python3
"""Push Community Node marker to OTS via CoT TCP.
Runs via cron every 4 hours to keep the marker visible on all EUDs."""

import socket
import datetime
import sys

HOST = "127.0.0.1"
PORT = 8088
LAT = "28.5565"
LON = "-81.1551"
HAE = "23"
CALLSIGN = "Community Node"
UID = "1cec9ca6-0b35-415f-9fd6-5aaf43094c79"
COT_TYPE = "a-f-G-U-C-S-M-N"
STALE_HOURS = 6

now = datetime.datetime.now(datetime.timezone.utc)
time_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")
stale_str = (now + datetime.timedelta(hours=STALE_HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")

cot = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<event version="2.0" uid="' + UID + '" type="' + COT_TYPE + '"'
    ' time="' + time_str + '" start="' + time_str + '" stale="' + stale_str + '"'
    ' how="h-g-i-g-o">'
    '<point lat="' + LAT + '" lon="' + LON + '" hae="' + HAE + '" ce="10" le="10"/>'
    '<detail>'
    '<contact callsign="' + CALLSIGN + '"/>'
    '<remarks>M2 Community Node - OpenTAK, Matrix, Monero, Mesh</remarks>'
    '<color argb="-16711936"/>'
    '<precisionlocation altsrc="DTED2" geopointsrc="USER"/>'
    '<usericon iconsetpath="m2-community-node-icons/Community Node/signal_unit.png"/>'
    '<link uid="' + UID + '" type="' + COT_TYPE + '" relation="p-p"/>'
    '</detail></event>'
)

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect((HOST, PORT))
    s.sendall(cot.encode())
    s.shutdown(socket.SHUT_WR)
    s.close()
    print(f"Marker pushed at {time_str}")
except Exception as e:
    print(f"Failed: {e}", file=sys.stderr)
    sys.exit(1)
