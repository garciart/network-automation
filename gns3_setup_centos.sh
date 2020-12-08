#!/usr/bin/bash
echo -e "Setting up GNS3..."
echo -e "Using:"
cat /etc/centos-release
echo -e "Updating CentOS"
sudo yum -y update
# Install GNS3 dependencies
sudo yum -y install python3 # Also installs python3-setuptools
sudo python3 -m pip install --upgrade pip
sudo python3 -m ensurepip
sudo yum -y install python3-devel
sudo yum -y install python3-tools
sudo yum -y install elfutils-libelf-devel # For Dynamips
sudo yum -y install libpcap-devel # For Dynamips
sudo yum -y install cmake # For Dynamips, VCPS, and ubridge
sudo yum -y install glibc-static # For VCPS
sudo yum -y install telnet # Yes, we will use Telnet
sudo yum -y install qt5-qtbase
sudo yum -y install qt5-qtbase-devel
sudo yum -y install qt5-qtsvg
sudo yum -y install qt5-qtsvg-devel
sudo yum -y install xterm # One of the consoles used by GNS
# Install GNS3
sudo python3 -m pip install gns3-server
sudo python3 -m pip install gns3-gui
sudo python3 -m pip install sip # For PyQT; used to bind C++ classes with Python
sudo python3 -m pip install pyqt5
sudo yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm # needed to install PuTTY and qemu
sudo yum -y install putty # Get from epel
sudo yum -y install qemu # Not qemu-kvm / get from epel
# Install the Dynamips Cisco Emulator
cd /tmp
git clone https://github.com/GNS3/dynamips.git
cd dynamips
mkdir build
cd build/
cmake .. -DDYNAMIPS_CODE=stable
make
sudo make install
# Install the Virtual PC Simulator (vpcs)
cd /tmp
sudo yum -y install svn
svn checkout http://svn.code.sf.net/p/vpcs/code/trunk vpcs
cd vpcs/src
./mk.sh 64
sudo install -m 755 vpcs /usr/local/bin
# Install ubridge to connect Ethernet, TAP interfaces, and UDP tunnels, as well as capture packets.
cd /tmp
git clone https://github.com/GNS3/ubridge.git
cd ubridge
make
sudo make install
# Get router image and configuration file
wget -P ~/GNS3/images/IOS http://tfr.org/cisco-ios/37xx/3745/c3745-adventerprisek9-mz.124-25d.bin
wget -P ~/Documents https://raw.githubusercontent.com/garciart/Automation/master/Linux/GNS3/R1_3745_i1_startup-config.cfg
# Used to create Tap interface between host and GNS3
sudo yum -y install bridge-utils
# Create a tap/loopback interface in Linux using the gns3_run.sh script
wget -P ~/Documents https://raw.githubusercontent.com/garciart/Automation/master/Linux/CentOS/gns3_run.sh
chmod +x gns3_run.sh
echo -e "Setup complete. Rebooting now..."
sudo reboot now