Deploy m2-status-bot to Pi #1 (comms, 192.168.8.10)
=====================================================

1. Copy scripts to Pi:
   scp scripts/m2-status-bot.sh ps@192.168.8.10:/tmp/
   scp scripts/m2-post-matrix.py ps@192.168.8.10:/tmp/

2. SSH to comms Pi and install:
   ssh ps@192.168.8.10
   sudo cp /tmp/m2-status-bot.sh /usr/local/bin/m2-status-bot.sh
   sudo cp /tmp/m2-post-matrix.py /usr/local/bin/m2-post-matrix.py
   sudo chmod +x /usr/local/bin/m2-status-bot.sh
   sudo chmod +x /usr/local/bin/m2-post-matrix.py

3. Copy systemd units:
   scp scripts/systemd/m2-status-bot.service ps@192.168.8.10:/tmp/
   scp scripts/systemd/m2-status-bot.timer ps@192.168.8.10:/tmp/

4. Install and enable timer (on comms Pi):
   sudo cp /tmp/m2-status-bot.service /etc/systemd/system/
   sudo cp /tmp/m2-status-bot.timer /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now m2-status-bot.timer

5. Test immediately:
   sudo systemctl start m2-status-bot.service
   journalctl -u m2-status-bot.service -f

6. Verify timer schedule:
   systemctl list-timers m2-status-bot.timer
