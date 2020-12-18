#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Script 63: Transfer files to flash using tftp (port 69).
Make sure GNS3 is running first (gns3_run.sh)

Also check that no 192.168.1.X addresses are in your ~/.ssh/known_hosts file.

Using Python 2.7.5
"""

"""
Other notes:
Check out https://linuxhint.com/install_tftp_server_centos7/
sudo yum install tftp tftp-server
systemctl diable firewalld
in.tftpd -s -l -c /var/lib/tftpboot
systemctl start tftp
systemctl status tftp
"""