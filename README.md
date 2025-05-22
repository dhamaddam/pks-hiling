Palm-Ganoderma Deployment Guide
📦 Setting Up Local Environment (Python 3.9)
bash
Copy
Edit
# Create and navigate to your environment directory
mkdir environtments
cd environtments

# Create virtual environment
python3 -m venv rest_serve

# Activate virtual environment
source environtments/rest_serve/bin/activate

# Install dependencies
pip3 install -r requirements.txt
📚 Install Required Python Modules
bash
Copy
Edit
pip3 install flask_sslify
pip3 install flask_restful
pip3 install flask
pip3 install redis
pip3 install scikit-learn
pip3 install pandas
pip3 install Flask-SSLify
pip3 install statsmodels
pip3 install matplotlib
pip3 install geopandas
pip3 install shapely
pip3 install flask_cors
pip3 install gunicorn
pip3 install openpyxl
🧪 Flask App Setup Using Python venv
Reference: DigitalOcean Flask Deployment Guide

bash
Copy
Edit
sudo apt update
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
sudo apt install python3-venv

# Project setup
mkdir ~/myproject
cd ~/myproject
cd ~/environtments
python3 -m venv environtments
🔒 Security and Additional Setup
bash
Copy
Edit
# Install essential security modules
pip install wheel
pip install uwsgi flask
pip3 install python-magic
If you encounter this error:
failed to find libmagic

Install the required package:

Ubuntu: sudo apt-get install libmagic1

Fedora: sudo yum install file

Mac: brew install libmagic

🚀 Creating and Running the App
bash
Copy
Edit
nano ~/environtments/main.py
Kill any process using port 5000:
bash
Copy
Edit
lsof -i :5000 | awk 'NR!=1 {print $2}' | xargs kill
🔐 Generate SSL PEM Certificate
bash
Copy
Edit
openssl req -x509 -newkey rsa:4096 -keyout palm-ganoderma/cert/key.pem -out palm-ganoderma/cert/cert.pem -days 365
Example:

Passphrase: 123ioprijaya

Common Name: iopri

PEM Passphrase: iopri

Optional: Remove PEM Passphrase
bash
Copy
Edit
openssl rsa -in original.key -out new.key
🔥 Run Flask App with Gunicorn
bash
Copy
Edit
gunicorn --bind 0.0.0.0:8000 wsgi:app
Check Gunicorn installation path:

bash
Copy
Edit
pip3 show gunicorn
🛠 Running as a Systemd Service
Place your project in:

bash
Copy
Edit
/usr/bin/palm-ganoderma/
Then link and enable the service:

bash
Copy
Edit
sudo ln -s /usr/bin/palm-ganoderma/ganoderma.service /lib/systemd/system/ganoderma.service
sudo systemctl daemon-reload
sudo systemctl enable ganoderma.service
sudo systemctl start ganoderma.service
sudo systemctl restart ganoderma.service
If the service file is updated:
bash
Copy
Edit
sudo systemctl daemon-reload
Gunicorn Run Command Example:

bash
Copy
Edit
/usr/bin/palm-ganoderma/environtments/rest_serve/bin/gunicorn -c /usr/bin/palm-ganoderma/gunicorn_config.py
🧹 Debugging and Logs
Nginx
bash
Copy
Edit
sudo truncate -s 0 /var/log/nginx/error.log
cat /var/log/nginx/error.log
sudo nano /etc/nginx/nginx.conf
sudo systemctl restart nginx
sudo nginx -t
Socket Permissions
bash
Copy
Edit
stat -c %U:%G /usr/bin/palm-ganoderma/ganoderma.sock
stat -c %a /usr/bin/palm-ganoderma/ganoderma.sock
sudo chown nginx:nginx /usr/bin/palm-ganoderma/ganoderma.sock
sudo chmod 660 /usr/bin/palm-ganoderma/ganoderma.sock
🐍 Install Python 3.9 (If Needed)
Follow this guide: Update Python 3 on CentOS - Vultr

🌐 Nginx Configuration
/etc/nginx/proxy_params
nginx
Copy
Edit
# proxy_params

proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_buffering off;
gzip off;
Main Configuration (/etc/nginx/nginx.conf)
nginx
Copy
Edit
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 4096;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    include /etc/nginx/conf.d/*.conf;

    server {
        listen       8080;
        listen       [::]:8080;
        server_name ganoderma.idiopri.xyz www.ganoderma.idiopri.xyz;

        location / {
            include proxy_params;
            proxy_pass http://unix:/usr/bin/palm-ganoderma/ganoderma.sock;
        }

        error_page 404 /404.html;
        location = /404.html {}

        error_page 500 502 503 504 /50x.html;
        location = /50x.html {}
        
        include /etc/nginx/sites-enabled/*;
    }

    # TLS Configuration block (optional)
}
