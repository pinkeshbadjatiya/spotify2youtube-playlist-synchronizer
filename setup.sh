sudo apt-get update
sudo apt-get install python-dev python-pip libpcre3 libpcre3-dev
sudo apt-get install uwsgi uwsgi-plugin-python
#pip install --user -U -I -r ./example_configurations/requirements.txt
sudo pip install -U -I -r ./example_configurations/requirements.txt
rm -rf configs && mkdir configs
cp ./example_configurations/config.ini.example ./configs/config.ini
cp ./example_configurations/api-listener.service.example ./configs/api-listener.service
cp ./example_configurations/api-listener.nginx.conf.example ./configs/api-listener.nginx.conf
cp ./example_configurations/client_secret_api-listener.json ./configs/client_secret_api-listener.json
cp ./example_configurations/users.txt.example ./configs/users.txt


echo '#################################################################################################'
echo '#################################################################################################'
echo '#####                                                                                       #####'
echo '#####   Setup NGINX and check its configuration for the domain api.armalcolite.ml           #####'
echo '#####                                                                                       #####'
echo '#####   >> Once Done pres any key to continue...                                            #####'
echo '#####                                                                                       #####'
echo '#################################################################################################'
echo '#################################################################################################'
read temp


echo '#################################################################################################'
echo '#################################################################################################'
echo '#####                                                                                       #####'
echo '#####   Setup NGINX and check its configuration for the domain api.armalcolite.ml           #####'
echo '#####                                                                                       #####'
echo '#################################################################################################'
echo '#################################################################################################'
read temp

echo '#################################################################################################'
echo '#################################################################################################'
echo '#####                                                                                       #####'
echo '#####   Update all the configs and then press enter to continue the setup.                  #####'
echo '#####                                                                                       #####'
echo '#####   1. Replace "<--APP_DIR--->" with the name of the folder in which the api-listener   #####'
echo '#####      is cloned.                                                                       #####'
echo '#####   2. Replace the "<--DOMAIN-->" with your domain name.                                #####'
echo '#####   3. Read all the config files in "<--APP_DIR--->/configs/" and make necessary        #####'
echo '#####      changes, especially the ones with replacing the "<--VARS-->".                    #####'
echo '#####   4. Add appropriate users in the configs/users.txt file as required.                 #####'
echo '#####                                                                                       #####'
echo '#####   >> Once Done pres any key to continue...                                            #####'
echo '#####                                                                                       #####'
echo '#################################################################################################'
read temp

echo '#################################################################################################'
echo '#################################################################################################'
echo '#####                                                                                       #####'
echo '#####   IMPORTANT: Modify configs/config.ini with the details about the developer           #####'
echo '#####              API credentials of various apps as required.                             #####'
echo '#####                                                                                       #####'
echo '#####   >> Once Done pres any key to continue...                                            #####'
echo '#####                                                                                       #####'
echo '#################################################################################################'
echo '#################################################################################################'
read temp

# If you are running it for the first time then run using the below command. This will save the google-auth-credentials in a file
# Try to add a song. Then it will save the credentials
echo '######################################################################################################'
echo '######################################################################################################'
echo '#####                                                                                            #####'
echo '#####   + Starting a temporary server to save the google-auth-credentials in file                #####'
echo '#####     "googlecredentials-oauth2.json".                                                       #####'
echo '#####   + Now open "http://localhost:8080/spotify2youtube?song=reality%20-%20lost%20frequencies" #####'
echo '#####     and the uwsgi will print a URL in logs which needs to be accessed to save the          #####'
echo '#####     credentials. It will then create file "googlecredentials-oauth2.json".                 #####'
echo '#####     NOTE: If you are running the server as a service on AWS or something,                  #####'
echo '#####           then you can fetch the "localhost:8090/***" URL on the remote machine            #####'
echo '#####           by making a reqest using CURL or WGET.                                           #####'
echo '#####                                                                                            #####'
echo '#####   >> Now press Ctrl+C once to kill the uwsgi instance and continue the setup.              #####'
echo '#####                                                                                            #####'
echo '######################################################################################################'
uwsgi --socket 0.0.0.0:8080 --protocol=http api-listener.ini

# To start the app using upstart
#sudo ln -s $PWD/configs/api-listener.upstart.conf /etc/init/    # Create a soft link for upstart in /etc/init
#sudo initctl reload-configuration   # Upstart does not reload configurations automatically for soft-links, so do it manually
#sudo start api-listener.service             # Start the api-listener app

# To start the app using systemd
sudo ln -s $PWD/configs/api-listener.service /etc/systemd/system/api-listener.service
sudo systemctl daemon-reload        # Reload systemctl cache
sudo systemctl start api-listener
sudo systemctl status api-listener
sudo systemctl enable api-listener

# Now attach the uwsgi app with nginx
# NOTE: Make sure you do not have anything else running on port 80
sudo ln -s $PWD/configs/api-listener.nginx.conf /etc/nginx/sites-enabled/
sudo service nginx restart
