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