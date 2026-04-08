#!/bin/bash
# m2-status-bot.sh — posts M2 service health digest to Matrix ops room
# Runs on Pi #1 (comms). Deploy to: /usr/local/bin/m2-status-bot.sh
# Systemd timer fires every 12h.
#
# DEPLOY NOTE: after copying to Pi #1, ensure /etc/hosts has:
#   192.168.8.20 atakenroll.yourdomain.com
# (Tailscale overrides resolv.conf on Pi #1 — local DNS overrides won't
# resolve without this hosts entry. Required for atakenroll cert check.)
#
# CONFIGURATION: set these in the environment or edit below before deploying.
# Values come from your M2_SECRETS.md (Matrix Bot section).

MATRIX_URL="${M2_MATRIX_URL:-https://m2-matrix.yourdomain.com}"
BOT_TOKEN="${M2_BOT_TOKEN:-CHANGE_ME}"
ROOM_ID="${M2_OPS_ROOM_ID:-CHANGE_ME}"
TACTICAL="192.168.8.20"
TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M UTC')

o() { echo "✅ $1"; }
w() { echo "⚠️  $1"; }
f() { echo "❌ $1"; }

container_local() {
    s=$(docker inspect --format '{{.State.Status}}' "$1" 2>/dev/null)
    [ "$s" = "running" ] && o "$1" || f "$1 (${s:-missing})"
}

container_remote() {
    s=$(ssh -o ConnectTimeout=5 -o BatchMode=yes pi@$TACTICAL \
        "docker inspect --format '{{.State.Status}}' $1" 2>/dev/null)
    [ "$s" = "running" ] && o "$1" || f "$1 (${s:-unreachable})"
}

systemd_remote() {
    s=$(ssh -o ConnectTimeout=5 -o BatchMode=yes pi@$TACTICAL \
        "systemctl is-active $1" 2>/dev/null)
    [ "$s" = "active" ] && o "$1" || f "$1 ($s)"
}

disk_local() {
    p=$(df / | awk 'NR==2{print $5}' | tr -d '%')
    [ "$p" -ge 90 ] && f "comms disk ${p}%" || \
    [ "$p" -ge 75 ] && w "comms disk ${p}%" || o "comms disk ${p}%"
}

disk_remote() {
    p=$(ssh -o ConnectTimeout=5 -o BatchMode=yes pi@$TACTICAL \
        "df / | awk 'NR==2{print \$5}'" 2>/dev/null | tr -d '%')
    [ -z "$p" ] && w "tactical disk (unreachable)" && return
    [ "$p" -ge 90 ] && f "tactical disk ${p}%" || \
    [ "$p" -ge 75 ] && w "tactical disk ${p}%" || o "tactical disk ${p}%"
}

cert_days() {
    d=$1
    p=${2:-443}
    exp=$(echo | timeout 5 openssl s_client -servername "$d" -connect "$d:$p" 2>/dev/null \
        | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    [ -z "$exp" ] && w "$d cert (check failed)" && return
    days=$(( ($(date -d "$exp" +%s) - $(date +%s)) / 86400 ))
    [ "$days" -lt 14 ] && f "$d cert ${days}d left" || \
    [ "$days" -lt 30 ] && w "$d cert ${days}d left" || o "$d cert ${days}d left"
}

LINE="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

MSG="M2 Node Status — $TIMESTAMP
$LINE
Pi #1 — comms
$(container_local community-node-conduit-1)
$(container_local community-node-nginx-1)
$(container_local community-node-element-web-1)
$(container_local community-node-cloudflared-1)
$(container_local community-node-tor-1)
$(container_local community-node-i2pd-1)
$(container_local adguard)
$(disk_local)
$LINE
Pi #2 — tactical
$(systemd_remote opentakserver)
$(container_remote tactical-node-headscale-1)
$(container_remote tactical-node-mosquitto-1)
$(systemd_remote mumble-server)
$(container_remote tactical-node-monerod-1)
$(disk_remote)
$LINE
Certificates
$(cert_days m2-matrix.yourdomain.com)
$(cert_days communitynode.yourdomain.com)
$(cert_days m2vpn.yourdomain.com)
$(cert_days atakenroll.yourdomain.com 8446)"

python3 /usr/local/bin/m2-post-matrix.py "$BOT_TOKEN" "$MATRIX_URL" "$ROOM_ID" "$MSG"
