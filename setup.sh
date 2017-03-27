sudo apt-get update
sudo apt-get install python-dev python-pip nginx uwsgi uwsgi-plugin-python
pip install -U -r configurations/requirements.txt
cd /home/grim/api.armalcolite.ml
mkdir configs
cp ./example_configurations/config.json.example ./configs/config.json
cp ./example_configurations/api-listener.service.example ./configs/api-listener.service
cp ./example_configurations/api-listener.nginx.conf.example ./configs/api-listener.nginx.conf
cp ./example_configurations/client_secret_api-listener.json ./configs/client_secret_api-listener.json

# If you are running it for the first time then run using the below command. This will save the google-auth-credentials in a file
uwsgi --socket 0.0.0.0:8080 --protocol=http api-listener.ini

# Now we need to start the app using upstart
#sudo ln -s $PWD/configs/api-listener.upstart.conf /etc/init/    # Create a soft link for upstart in /etc/init
#sudo initctl reload-configuration   # Upstart does not reload configurations automatically for soft-links, so do it manually
#sudo start api-listener.service             # Start the api-listener app

sudo ln -s $PWD/configs/api-listener.service /etc/systemd/system/api-listener.service
sudo systemctl daemon-reload        # Reload systemctl cache
sudo systemctl start api-listener
sudo systemctl status api-listener
sudo systemctl enable api-listener


# Now attach the uwsgi app with nginx
# NOTE: Make sure you do not have anything else running on port 80
sudo ln -s $PWD/configs/api-listener.nginx.conf /etc/nginx/sites-enabled/
sudo service nginx restart

