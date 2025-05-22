create env and install local environtment 
using python3.9 version
# mkdir environtments
# cd environtments
# python3 -m venv rest_serve
# source environtments/rest_serve/bin/activate
# pip3 install -r requirements.txt

install module 
# pip3 install flask_sslify
# pip3 install flask_restful
# pip3 install flask
# pip3 install redis
# pip3 install scikit-learn
# pip3 install pandas
# pip3 install Flask-SSLify
# pip3 install statsmodels
# pip3 install matplotlib
# pip3 install geopandas
# pip3 install shapely
install flask with python venv 
https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04
# sudo apt update
# sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
# sudo apt install python3-venv
# mkdir ~/myproject
# cd ~/myproject
# cd ~/environtments 
# python3 -m venv environtments

setting up flask 

# pip install wheel
# pip install uwsgi flask

setting for security reason 

# pip3 install python-magic

if error "failed to find libmagic"

# sudo apt-get install libmagic1 --Ubuntu
# sudo yum install file --on fedora
# brew install libmagic --mac

creating an App

# nano ~/environtments/main.py

kill all process that use port 5000

# lsof -i :5000 | awk 'NR!=1 {print $2}' | xargs kill

install cors 

generate pem certificate 
# openssl req -x509 -newkey rsa:4096 -keyout palm-ganoderma/cert/key.pem -out palm-ganoderma/cert/cert.pem -days 365

# Enter PEM pass phrase: 123ioprijaya
# Common Name (e.g. server FQDN or YOUR name) []: iopri

# pip3 install flask_cors 

PEM pass phrase :  iopri

Remove the Passphrase (Optional):
If you find it inconvenient to enter the passphrase each time you start the Flask application, you can remove the passphrase from the private key

Use the following command to create a new private key file without a passphrase:

# openssl rsa -in original.key -out new.key

Release Port 5000:

If you cannot identify the program using port 5000 and need to use that port, you can release the port using the following command:

# sudo lsof -t -i:5000 | xargs kill -9

Gunicorn to serve your Flask application with a custom domain : 

# pip3 install gunicorn
# pip3 install openpyxl


Another note, there is a service file to run this program as service. To make it works, you need to put this program inside **/usr/bin/** folder, so the program path will be **/usr/bin/palm-ganoderma/**. After that you need to link the service file to folder **/lib/systemd/system/** by executing:

```sh
sudo ln -s /usr/bin/bots/palm-ganoderma/ganoderma.service /lib/systemd/system/ganoderma.service
sudo systemctl daemon-reload
```

After that, try to run and enable (on startup) the service

```sh
sudo systemctl enable ganoderma.service
sudo systemctl start ganoderma.service
sudo systemctl restart ganoderma.service
systemctl daemon-reload
```

If service file changed, you need to reload the daemon service

```sh
sudo systemctl daemon-reload
```

The only required argument to Gunicorn tells it how to load your Flask application. The syntax is {module_import}:{app_variable}. module_import is the dotted import name to the module with your application. app_variable is the variable with the application. It can also be a function call (with any arguments) if you’re using the app factory pattern.

# /usr/bin/bots/palm-ganoderma/environtments/rest_serve/bin/gunicorn -c /usr/bin/bots/palm-ganoderma/gunicorn_config.py 

run on server
# gunicorn --bind 0.0.0.0:8000 wsgi:app

showing where gunicorn was installed
# pip3 show gunicorn


debugging nginx 
# sudo truncate -s 0 /var/log/nginx/error.log
# cat /var/log/nginx/error.log
# sudo nano /etc/nginx/nginx.conf
# sudo systemctl restart nginx
# sudo systemctl restart nginx
# sudo nginx -t
# stat -c %U:%G /usr/bin/bots/palm-ganoderma/ganoderma.sock
# stat -c %a /usr/bin/bots/palm-ganoderma/ganoderma.sock
# sudo chown nginx:nginx /usr/bin/bots/palm-ganoderma/ganoderma.sock
# sudo chmod 660 /usr/bin/bots/palm-ganoderma/ganoderma.sock

debugging gunicorn


# install python3.9 
https://vultr.com/docs/update-python3-on-centos/

for uploading to server 

put this in to `` /etc/nginx/proxy_params ``
`` # proxy_params

# Common proxy headers
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
# Buffering off for long-lived connections
proxy_buffering off;

# Disable gzip for clients that don't support it
gzip off; ``

-- WITH NGINX configuration.

``
# For more information on configuration, see:
#   * Official English Documentation: http://nginx.org/en/docs/
#   * Official Russian Documentation: http://nginx.org/ru/docs/

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

# Load dynamic modules. See /usr/share/doc/nginx/README.dynamic.
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

    #include /etc/nginx/sites-enabled/*;

    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See http://nginx.org/en/docs/ngx_core_module.html#include
    # for more information.
    include /etc/nginx/conf.d/*.conf;

    server {
        listen       8080;
        listen       [::]:8080;
        
        server_name ganoderma.idiopri.xyz www.ganoderma.idiopri.xyz;

        # Load configuration files for the default server block.
        #include /etc/nginx/default.d/*.conf;
        location / {
                include proxy_params;
                proxy_pass http://unix:/usr/bin/bots/palm-ganoderma/ganoderma.sock;

#               proxy_pass http://127.0.0.1:8000;  # Adjust the address and port based on your Gunicorn configuration
#               proxy_set_header Host $host;
#               proxy_set_header X-Real-IP $remote_addr;
#               proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        error_page 404 /404.html;
        location = /404.html {
        }

        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
        }

        include /etc/nginx/sites-enabled/*;
    }

# Settings for a TLS enabled server.
#
#    server {
#        listen       443 ssl http2;
#        listen       [::]:443 ssl http2;
#        server_name  _;
#        root         /usr/share/nginx/html;
#
#        ssl_certificate "/etc/pki/nginx/server.crt";
#        ssl_certificate_key "/etc/pki/nginx/private/server.key";
#        ssl_session_cache shared:SSL:1m;
#        ssl_session_timeout  10m;
#        ssl_ciphers HIGH:!aNULL:!MD5;
#        ssl_prefer_server_ciphers on;
#
#        # Load configuration files for the default server block.
#        include /etc/nginx/default.d/*.conf;
#
#        error_page 404 /404.html;
#            location = /40x.html {
#        }
#
#        error_page 500 502 503 504 /50x.html;
#            location = /50x.html {
#        }
#    }

# }