# Becker Screenshot Autocropper


### Configure the database

Create a `config.py` file with the PostgreSQL connection details.

```
DATABASE_HOST = '111.111.111.111'
DATABASE_NAME = 'becker_screenshot_autocropper'
DATABASE_USER ='YOUR_USER_HERE'
DATABASE_PASSWORD = 'YOUR_PASSWORD_HERE'
```

### Running the app

```bash
python app.py
```

### Running the app with `gunicorn`

```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

### Setting up the service

File: `/etc/systemd/system/becker.service`

#### Using `gunicorn` without binding to a Unix socket

```
[Unit]
Description=Gunicorn instance to serve the Becker screenshot autocropper app
After=network.target

[Service]
WorkingDirectory=/var/www/becker-screenshot-autocropper
Environment="PATH=/root/miniforge3/envs/gies/bin"
ExecStart=/root/miniforge3/envs/gies/bin/gunicorn --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Using `gunicorn` and bind to a Unix socket

Use this configuration to serve the app through Nginx or Apache.

```
[Unit]
Description=Gunicorn instance to serve the Becker screenshot autocropper app
After=network.target

[Service]
WorkingDirectory=/var/www/becker-screenshot-autocropper
Environment="PATH=/root/miniforge3/envs/gies/bin"
ExecStart=/root/miniforge3/envs/gies/bin/gunicorn --bind unix:becker.sock -m 777 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Start or stop service

Start and enable the service.

```bash
sudo systemctl start becker
sudo systemctl enable becker
```

Check status of the service.

```bash
sudo systemctl status becker
```

Stop the service.

```bash
sudo systemctl stop becker
```

### Nginx setup

File: `/etc/nginx/sites-available/becker`

```
server {
    listen: 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/becker-screenshot-autocropper/becker.sock;
    }
}
```

Create a symbolic link to the configuration file.

```bash
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
```

Test the Nginx configuration.

```bash
sudo nginx -t
```

```bash
sudo systemctl restart nginx
sudo ufw allow 'Nginx Full'
```

Check [this DigitalOcean tutorial](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-22-04) for details on how to add a SSL certificate.

