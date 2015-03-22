#!/usr/bin/env bash

# add mongo repositories
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list

apt-get update

# Python dev packages
apt-get install -y build-essential python python-dev python-setuptools python-pip

# Git (we'd rather avoid people keeping credentials for git commits in the repo, but sometimes we need it for pip requirements that aren't in PyPI)
apt-get install -y git

# install python 2.7.9 
wget http://python.org/ftp/python/2.7.9/Python-2.7.9.tar.xz
tar xf Python-2.7.9.tar.xz
cd Python-2.7.9
./configure --prefix=/usr/local
make && make altinstall

#install pip with 2.7.9
cd /home/vagrant
wget https://bootstrap.pypa.io/get-pip.py
/usr/local/bin/python2.7 get-pip.py

#install mongo
apt-get install -y mongodb-org
sed -i 's/127.0.0.1/0.0.0.0/' /etc/mongod.conf
service mongod restart