"""
Generate ATAK data package for M2 Community Node server enrollment.
Produces atak-connect.zip — host on nginx, user downloads and opens with ATAK.
One scan → download → import → connected. No manual cert steps.

Usage: python make_atak_dp.py
Output: /var/www/html/opentakserver/atak-connect.zip
"""

import zipfile
import uuid
import os

# ── Config ────────────────────────────────────────────────────────────────────
SERVER_IP = "192.168.8.20"
SERVER_PORT = "8089"
SERVER_PROTOCOL = "ssl"
SERVER_NAME = "M2 Community Node"
TRUSTSTORE_SRC = "/home/pi/ots/ca/truststore-root.p12"   # adjust to match your Linux username
TRUSTSTORE_PASS = "atakatak"                               # OTS vendor default — change if rotated
OUTPUT_PATH = "/var/www/html/opentakserver/atak-connect.zip"
DOWNLOAD_PORT = "8447"  # HTTPS static server — no client cert, no "not downloaded securely" warning
ENROLL_USER = "CHANGE_ME"   # OTS enrollment username
ENROLL_PASS = "CHANGE_ME"   # OTS enrollment password
# ── End Config ────────────────────────────────────────────────────────────────

# UUID used as both package UID and subdirectory name inside the zip
PACKAGE_UID = str(uuid.uuid4())
SUBDIR = PACKAGE_UID

# On-device paths where ATAK extracts the files
ATAK_CERT_PATH = "/storage/emulated/0/atak/cert/truststore-root.p12"
ATAK_PREF_PATH = "/storage/emulated/0/atak/config/prefs/preference.pref"

CONNECT_STRING = f"{SERVER_IP}:{SERVER_PORT}:{SERVER_PROTOCOL}"

MANIFEST = f"""<?xml version="1.0" encoding="UTF-8"?>
<MissionPackageManifest version="2">
   <Configuration>
      <Parameter name="uid" value="{PACKAGE_UID}"/>
      <Parameter name="name" value="{SERVER_NAME} Connection"/>
   </Configuration>
   <Contents>
      <Content ignore="false" zipEntry="{SUBDIR}/truststore-root.p12">
         <Parameter name="localpath" value="{ATAK_CERT_PATH}"/>
      </Content>
      <Content ignore="false" zipEntry="{SUBDIR}/preference.pref">
         <Parameter name="localpath" value="{ATAK_PREF_PATH}"/>
      </Content>
   </Contents>
</MissionPackageManifest>"""

PREFERENCE = f"""<?xml version='1.0' standalone='yes'?>
<preferences>
  <preference version="1" name="com.atakmap.app_preferences">
    <entry key="displayServerConnectionWidget" class="class java.lang.Boolean">true</entry>
  </preference>
  <preference version="1" name="cot_streams">
    <entry key="count" class="class java.lang.Integer">1</entry>
    <entry key="description0" class="class java.lang.String">{SERVER_NAME}</entry>
    <entry key="enabled0" class="class java.lang.Boolean">true</entry>
    <entry key="connectString0" class="class java.lang.String">{CONNECT_STRING}</entry>
    <entry key="caLocation0" class="class java.lang.String">{ATAK_CERT_PATH}</entry>
    <entry key="caPassword0" class="class java.lang.String">{TRUSTSTORE_PASS}</entry>
    <entry key="enrollForCertificateWithTrust0" class="class java.lang.Boolean">true</entry>
    <entry key="useAuth0" class="class java.lang.Boolean">true</entry>
    <entry key="cacheCreds0" class="class java.lang.String">cache</entry>
    <entry key="username0" class="class java.lang.String">{ENROLL_USER}</entry>
    <entry key="password0" class="class java.lang.String">{ENROLL_PASS}</entry>
    <entry key="compress0" class="class java.lang.Boolean">false</entry>
  </preference>
</preferences>"""


def main():
    if not os.path.exists(TRUSTSTORE_SRC):
        print(f"ERROR: Truststore not found at {TRUSTSTORE_SRC}")
        return

    with zipfile.ZipFile(OUTPUT_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("MANIFEST/manifest.xml", MANIFEST)
        zf.writestr(f"{SUBDIR}/preference.pref", PREFERENCE)
        zf.write(TRUSTSTORE_SRC, f"{SUBDIR}/truststore-root.p12")

    size = os.path.getsize(OUTPUT_PATH)
    print(f"Generated: {OUTPUT_PATH} ({size} bytes)")
    print(f"Download URL: https://{SERVER_IP}:{DOWNLOAD_PORT}/atak-connect.zip")
    print(f"Package UID: {PACKAGE_UID}")


if __name__ == "__main__":
    main()
