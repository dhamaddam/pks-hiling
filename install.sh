#!/bin/bash
#source /usr/bin/bots/pks-hiling/environtments/rest_serve/bin/activate
pip3 install -r requirements.txt
sudo mkdir /etc/nginx/sites-available
sudo cp /usr/bin/bots/pks-hiling/site-available/pks-hiling.xyz /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/pks-hiling.xyz /etc/nginx/sites-enabled/pks-hiling.xyz
sudo nginx -t
sudo systemctl restart nginx
sudo ln -s /usr/bin/bots/pks-hiling/pks-hiling.service /lib/systemd/system/pks-hiling.service
sudo cp /usr/bin/bots/pks-hiling/config.ini.dist /usr/bin/bots/pks-hiling/config.ini
chown www-data:ubuntu /bin/bots/pks-hiling/*
chown www-data:ubuntu /usr/bin/bots/pks-hiling/logs/*
sudo systemctl daemon-reload
sudo systemctl start pks-hiling
sudo systemctl enable pks-hiling
