import sys

import pexpect

from cisco_ios import CiscoIOS
from labs.cisco.reporter import Reporter
from labs.cisco.utility import (enable_ftp, disable_ftp, )

switch = CiscoIOS('Switch')
reporter = Reporter()
child = pexpect.spawn('telnet 192.168.1.1 5003')
child.delaybeforesend = 0.5
child.logfile = sys.stdout
child.sendline('copy running-config startup-config')
child.expect_exact('Destination filename')
child.sendline('startup-config')
child.expect_exact('[OK]')
child.expect_exact('Switch#')
enable_ftp('gns3user')

switch.download_file_ftp(child, reporter, eol='',
                         device_file_system='nvram',
                         remote_ip_addr='192.168.1.10',
                         remote_username='gns3user',
                         file_to_download='startup-config',
                         destination_filepath='switch-confg',
                         remote_password='gns3user')
switch.upload_file_ftp(child, reporter, eol='',
                       device_file_system='flash0',
                       remote_ip_addr='192.168.1.10',
                       remote_username='gns3user',
                       file_to_upload='switch-confg',
                       destination_filepath='switch-confg',
                       remote_password='gns3user')
disable_ftp('gns3user')

"""
/usr/bin/python2.7 /home/gns3user/network-automation/labs/cisco/test.py
copy running-config startup-config
Trying 192.168.1.1...
Connected to 192.168.1.1.
Escape character is '^]'.
copy running-config startup-config
Destination filename [startup-startup-config
config]? startup-config
Building configuration...
Compressed configuration from 3428 bytes to 1585 bytes[OK]
Switch#Step: Downloading startup-config from the device using FTP...
;1651852218

*May  6 15:45:40.571: %GRUB-5-CONFIG_WRITING: GRUB configuration is being updated on disk. Please wait...
*May  6 15:45:41.269: %GRUB-5-CONFIG_WRITTEN: GRUB configuration was written to disk successfully.;1651852218
Switch#

Switch#configure terminal
configure terminal
Enter configuration commands, one per line.  End with CNTL/Z.
Switch(config)#ip ftp username gns3user
ip ftp username gns3user
Switch(config)#ip ftp password gns3user
ip ftp password gns3user
Switch(config)#end
end
Switch#copy nvram: ftp:
copy nvram: ftp:
Source filenamestartup-config
 []? startup-config
*May  6 15:45:54.569: %SYS-5-CONFIG_I: Configured from console by console
Address or name of remote host192.168.1.10
 []? 192.168.1.10
Destination filename [switch-cswitch-confg
onfg]? switch-confg
Writing switch-confg !
3428 bytes copied in 0.090 secs (38089 bytes/sec)
Switch#[OK]
Step: Uploading switch-confg to the device using FTP...
;1651852234
;1651852234
Switch#

Switch#configure terminal
configure terminal
Enter configuration commands, one per line.  End with CNTL/Z.
Switch(config)#ip ftp username gns3user
ip ftp username gns3user
Switch(config)#ip ftp password gns3user
ip ftp password gns3user
Switch(config)#end
end
Switch#copy ftp: flash0:
copy ftp: flash0:
Address or name of remote host192.168.1.10
 []? 192.168.1.10
*May  6 15:46:09.516: %SYS-5-CONFIG_I: Configured from console by console
Source filename []?switch-confg
 switch-confg
Destination filename [switch-cswitch-confg
onfg]? switch-confg
Accessing ftp://192.168.1.10/switch-confg...
Loading switch-confg !
[OK - 3428/4096 bytes]

3428 bytes copied in 0.628 secs (5459 bytes/sec)
Switch#[OK]

Process finished with exit code 0
"""
