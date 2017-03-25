echo "Run with SUDO! to allow changing owner of log file"
sudo initctl reload-configuration
sudo service api-listener restart
#chown ubuntu:ubuntu /var/log/upstart/api-listener.log
