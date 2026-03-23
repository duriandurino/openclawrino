#!/bin/bash
# Watchdog Implementation

# Setting up Watchdog in Bootconfig
echo 'Setting up Watchdog in Bootconfig';
sleep 2;
sudo echo 'dtparam=watchdog=on' >> /boot/config.txt

# Installing Watchdog
echo 'Installing Watchdog';
sleep 2;
sudo apt update --assume-yes;
sudo apt install watchdog --assume-yes;

# Setting Watchdog Configs
echo 'Setting Watchdog Configs';
sleep 2;
echo 'watchdog-device = /dev/watchdog' | sudo tee -a /etc/watchdog.conf
echo 'watchdog-timeout = 15' | sudo tee -a /etc/watchdog.conf
echo 'max-load-1 = 24'| sudo tee -a /etc/watchdog.conf

# Setting Watchdog as a Service
echo 'Setting Watchdog as a Service';
sleep 2;
sudo systemctl enable watchdog
sudo systemctl start watchdog

# Restarting
echo 'Done, now run the crash simulator command';
