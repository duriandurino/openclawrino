echo "> Starting PM2";
sleep 2;
pm2 start /home/pi/n-compasstv/ecosystem.config.js --only player-server;
sleep 2;
pm2 startup;
sudo env PATH=$PATH:/usr/local/bin /usr/local/lib/node_modules/pm2/bin/pm2 startup systemd -u pi --hp /home/pi;
sleep 1;
pm2 save;