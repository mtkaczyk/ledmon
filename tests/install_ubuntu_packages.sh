#!/usr/bin/bash

# Add ubuntu repository
sudo add-apt-repository "deb [arch=amd64] http://archive.ubuntu.com/ubuntu focal main universe"
# Install gcc
sudo apt-get update && sudo apt-get install gcc-$1 g++-$1
# Install dependencies
sudo apt-get install pkg-config automake autoconf autoconf-archive make libsgutils2-dev \
        libudev-dev libpci-dev check
