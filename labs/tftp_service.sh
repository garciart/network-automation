#!/bin/bash
shopt -s -o nounset
# Script to enable and disable TFTP service
# Usage: ./tftp_service.sh enable /var/lib/tftpboot/R1_7206_i1_startup-config.cfg
# Usage: ./tftp_service.sh disable
# Don't forget to set this script's permissions to executable!
# sudo chmod 755 tftp_service.sh

if [ "$1" == "enable" ] && [ "$#" == 2 ]
then
  echo "Enabling TFTP service."
  sudo mkdir -p -m755 /var/lib/tftpboot
  sudo chmod 755 /var/lib/tftpboot
  exists=$(ls "$2")
  if [ -n "$exists" ]
  then
    permissions=$(stat -c %a "$2")
    if [ "$permissions" -lt 666 ]
    then
      chmod 666 "$2"
    fi
    sudo chmod u+w /etc/xinetd.d/tftp
    sudo sed -i 's|server_args *= -s /var/lib/tftpboot|server_args             = -c -s /var/lib/tftpboot|g' /etc/xinetd.d/tftp
    sudo sed -i 's|disable *= yes|disable                 = no|g' /etc/xinetd.d/tftp
    sudo firewall-cmd --zone=public --add-service=tftp
    sudo systemctl start tftp
    sudo systemctl enable tftp
  fi
elif [ "$1" == "disable" ]
then
  echo "Disabling TFTP service."
  sudo sed -i 's|server_args *= -c -s /var/lib/tftpboot|server_args             = -s /var/lib/tftpboot|g' /etc/xinetd.d/tftp
  sudo sed -i 's|disable *= no|disable                 = yes|g' /etc/xinetd.d/tftp
  sudo chmod 644 /etc/xinetd.d/tftp
  sudo firewall-cmd --zone=public --remove-service=tftp
  sudo systemctl stop tftp
  sudo systemctl disable tftp
# elif [ "$1" == "-h" ] || [ "$1" == "--help" ] || [ -z "$1" ]; then
else
  echo "Enables and disables the TFTP service."
  echo "Usage:"
  echo "  (To enable):  ./tftp_service.sh enable /var/lib/tftpboot/<configuration file name>"
  echo "  (To disable): ./tftp_service.sh disable"
fi
