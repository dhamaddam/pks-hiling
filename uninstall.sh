#!/bin/bash
sudo systemctl stop pks-hiling.service
sudo systemctl disable pks-hiling.service
sudo rm -rf /lib/systemd/system/pks-hiling.service
sudo systemctl daemon-reload