#!/bin/sh
# Guest network firewall rules — allow guest (192.168.9.x) to reach
# specific services on the LAN (192.168.8.x). All other guest→lan
# traffic remains blocked. These rules persist across reboots via UCI.
#
# Prerequisites: GL.iNet router with guest zone configured.
# Run once after factory reset or firmware upgrade.

# Forwarding: allow guest→lan traffic (individual rules below control which ports)
# Without this, fw4 has no guest_to_lan chain and per-port rules fail with "null_to_lan"
uci add firewall forwarding
uci set firewall.@forwarding[-1].src='guest'
uci set firewall.@forwarding[-1].dest='lan'

# Pi #1 (comms 192.168.8.10) — Element Web
uci add firewall rule
uci set firewall.@rule[-1].name='guest_element_web'
uci set firewall.@rule[-1].src='guest'
uci set firewall.@rule[-1].dest='lan'
uci set firewall.@rule[-1].dest_ip='192.168.8.10'
uci set firewall.@rule[-1].dest_port='8080'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'

# Pi #1 (comms 192.168.8.10) — Kiosk / visitor page
uci add firewall rule
uci set firewall.@rule[-1].name='guest_kiosk_page'
uci set firewall.@rule[-1].src='guest'
uci set firewall.@rule[-1].dest='lan'
uci set firewall.@rule[-1].dest_ip='192.168.8.10'
uci set firewall.@rule[-1].dest_port='8081'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'

# Pi #1 (comms 192.168.8.10) — Matrix HTTPS / federation
uci add firewall rule
uci set firewall.@rule[-1].name='guest_matrix_https'
uci set firewall.@rule[-1].src='guest'
uci set firewall.@rule[-1].dest='lan'
uci set firewall.@rule[-1].dest_ip='192.168.8.10'
uci set firewall.@rule[-1].dest_port='443'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'

# Pi #2 (tactical 192.168.8.20) — Monero restricted RPC
uci add firewall rule
uci set firewall.@rule[-1].name='guest_monero_rpc'
uci set firewall.@rule[-1].src='guest'
uci set firewall.@rule[-1].dest='lan'
uci set firewall.@rule[-1].dest_ip='192.168.8.20'
uci set firewall.@rule[-1].dest_port='18089'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'

# Pi #2 (tactical 192.168.8.20) — OpenTAK CoT
uci add firewall rule
uci set firewall.@rule[-1].name='guest_opentak_cot'
uci set firewall.@rule[-1].src='guest'
uci set firewall.@rule[-1].dest='lan'
uci set firewall.@rule[-1].dest_ip='192.168.8.20'
uci set firewall.@rule[-1].dest_port='8088'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'

# Pi #2 (tactical 192.168.8.20) — OpenTAK Web UI (guest map access)
uci add firewall rule
uci set firewall.@rule[-1].name='guest_opentak_webui'
uci set firewall.@rule[-1].src='guest'
uci set firewall.@rule[-1].dest='lan'
uci set firewall.@rule[-1].dest_ip='192.168.8.20'
uci set firewall.@rule[-1].dest_port='8080'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'

# Commit and reload
uci commit firewall
/etc/init.d/firewall reload

echo "Guest firewall rules applied successfully."
