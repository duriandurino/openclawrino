#!/bin/bash

## Update and Upgrade
echo ">> System Update and Upgrade";
sudo apt update -y && sudo apt upgrade -y;

## Installing required system apps
# NGINX
echo ">> Installing NGINX";
sudo apt install nginx -y;

# NodeJS and NPM (Upgraded to Node 20 for Pi 5/Trixie compatibility)
echo ">> Installing NodeJS 20";
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2

# Chromium (Modern package name)
echo ">> Installing Chromium";
sudo apt install chromium -y;

# GNome Terminal
echo ">> Installing Gnome Terminal";
sudo apt install gnome-terminal -y;

# SCROT and Unclutter
echo ">> Installing SCROT and Unclutter";
sudo apt install scrot unclutter -y;

# CEC Utils
echo ">> Installing CEC Utils";
sudo apt install cec-utils -y;

## Creating Required Folders
echo ">> Cleaning old folders"
sudo rm -rf /home/pi/n-compasstv;
sudo rm -rf /var/www/html/*;

echo ">> Creating Required Folders";
sudo mkdir -p /var/www/html/ui
sudo mkdir -p /var/www/html/assets
sudo chmod -R 777 /var/www/html
mkdir -p /home/pi/n-compasstv/player-server
sudo chmod -R 777 /home/pi/n-compasstv

## Installing the Player App
echo ">> Downloading Player Server";
# Using the files you already have or downloading if missing
if [ ! -f /home/pi/player-server-2.6.0.zip ]; then
    curl -O https://ncompasstv-prod-player-apps.s3.amazonaws.com/player-server-2.6.0.zip
fi
unzip -o /home/pi/player-server-2.6.0.zip -d /home/pi/n-compasstv/
# Handle the nested folder structure from unzip
if [ -d /home/pi/n-compasstv/player-server-2.6.0 ]; then
    cp -r /home/pi/n-compasstv/player-server-2.6.0/* /home/pi/n-compasstv/player-server/
    rm -rf /home/pi/n-compasstv/player-server-2.6.0
fi

echo ">> Installing Player Server NPM Modules (Fixing node-gyp)";
cd /home/pi/n-compasstv/player-server/
# Force update node-gyp to fix the Python 'rU' error
npm install node-gyp@latest
npm install

echo ">> Download Player UI";
cd /home/pi
if [ ! -f /home/pi/player-ui-2.4.1.zip ]; then
    curl -O https://ncompasstv-prod-player-apps.s3.amazonaws.com/player-ui-2.4.1.zip
fi
unzip -o /home/pi/player-ui-2.4.1.zip -d /var/www/html/ui
sudo chmod -R 777 /var/www/html/ui

## Moving over necessary config files
echo ">> Copying PM2 Ecosystem Config File";
[ -f /home/pi/nctv-installer/ecosystem.config.js ] && cp /home/pi/nctv-installer/ecosystem.config.js /home/pi/n-compasstv/

echo ">> Copying NGINX Config";
sudo cp /home/pi/nctv-installer/nginx.conf /etc/nginx/nginx.conf

echo ">> Creating Desktop Config Paths for Pi 5";
mkdir -p /home/pi/.config/lxpanel/LXDE-pi/panels/
[ -f /home/pi/nctv-installer/panel ] && cp /home/pi/nctv-installer/panel /home/pi/.config/lxpanel/LXDE-pi/panels/

echo ">> Setting Wallpaper";
mkdir -p /home/pi/Pictures
[ -f /home/pi/nctv-installer/rpiBG.png ] && cp /home/pi/nctv-installer/rpiBG.png /home/pi/Pictures/

echo ">> Setup Complete. Rebooting...";
sleep 2
sudo reboot
