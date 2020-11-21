#!/usr/bin/bash
echo -e "Setting up GNS3..."
# Get and save the original IP address that can connect to the Internet (should be enp0s3 or eth0)
org_interface=$(ip route get 8.8.8.8 | awk -F"dev " 'NR==1{split($2,a," ");print a[1]}')
org_ip=$(ip route get 8.8.8.8 | awk -F"src " 'NR==1{split($2,a," ");print a[1]}')
org_netmask=$(ifconfig $org_interface | grep -w inet | awk '{print $4}' | cut -d ":" -f 2)
org_broadcast=$(ifconfig $org_interface | grep -w inet | awk '{print $6}' | cut -d ":" -f 2)
echo "Original interface name is $org_interface"
echo "$org_interface original IP address is $org_ip"
echo "$org_interface original netmask is $org_netmask"
echo "$org_interface original broadcast address is $org_broadcast"
sudo ip tuntap add tap0 mode tap # Add the tap device
sudo ifconfig tap0 0.0.0.0 promisc up # Configure the tap
sudo ifconfig $org_interface 0.0.0.0 promisc up # Zero out the default Ethernet connection
sudo brctl addbr br0 # Create the bridge
sudo brctl addif br0 tap0 # Add the tap to the bridge
sudo brctl addif br0 $org_interface # Add the default Ethernet connection to the bridge
sudo ifconfig br0 up # Start the bridge
sudo ifconfig br0 192.168.1.99/24 # Configure the bridge
sudo route add default gw 192.168.1.254 # Setup the default gateway
echo
echo -e "Network interface configuration:"
ifconfig # Verify the devices exist
echo
echo -e "Bridge information:"
sudo brctl show # Verify the bridge is set up
echo
echo -e "Starting GNS3..."
gns3 # Start GNS3
# Upon exit from GNS3, reset the default Ethernet connection to access the Internet
sudo ifconfig br0 down # Stop the bridge
sudo brctl delif br0 $org_interface # Remove the default Ethernet connection from the bridge
sudo brctl delif br0 tap0 # Remove the tap from the bridge
sudo brctl delbr br0 # Delete the bridge
sudo ifconfig tap0 down # Stop the tap
sudo ip link delete tap0 # Delete the tap
# Reset the default Ethernet connection
echo
echo -e "Resetting the network (please wait 30 seconds...)"
sudo ifconfig $org_interface -promisc
sudo ifconfig $org_interface $org_ip up
sudo ifconfig $org_interface netmask $org_netmask
sudo ifconfig $org_interface broadcast $org_broadcast
# sudo /etc/init.d/network restart
sudo systemctl restart network
sleep 30
sudo systemctl status network
ifconfig # Verify the result
echo -e "Script complete. Have a nice day."