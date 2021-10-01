# Adventures in Network Automation

## Lab 000 - Complete Automation Lab

This lab combines all the labs into a single, executable script.

***Notes:***

Before transferring files between the CentOS host and Cisco devices, you must install the following files on the host:

- ```tftp``` and ```tftp-server``` - The Trivial File Transfer Protocol (TFTP) Client and Server is a simple file transfer protocol. Data transferred over UDP is not encrypted and is insecure. In addition, since TFTP uses the User Datagram Protocol (UDP), there are no transmission integrity checks, such as handshaking. However, TFTP is adequate for small file transfers, such transferring a configuration file between a host and a device over a dedicated line. For more information, see [the Wikipedia entry for TFTP](https://en.wikipedia.org/wiki/Trivial_File_Transfer_Protocol "TFTP") and [the Wikipedia entry for UDP](https://en.wikipedia.org/wiki/User_Datagram_Protocol "UDP").

```
sudo yum -y install tftp tftp-server* 
sudo mkdir -p /var/lib/tftpboot
sudo chmod 777 /var/lib/tftpboot
```

You may also want to install:
 
- ```xinetd``` - The Extended Internet Service Daemon (xinetd) listens for incoming requests over a network, using port numbers as identifiers, and launches the appropriate service for that request. For example, if xinetd hears a request over User Datagram Protocol (UDP) port 69, it will launch the Trivial File Transfer Protocol (TFTP) service. For more information, see [the Wikipedia entry for xinetd](https://en.wikipedia.org/wiki/Xinetd "xinetd").

```
sudo yum -y install xinetd*
```

In addition, CentOS 7 runs Security-Enhanced Linux (SELinux) in enforcing mode by default, which may prevent you from using insecure file transfer protocols, such as TFTP:

```
$ sestatus | grep "mode\|Mode"
Current mode:                   enforcing
Mode from config file:          enforcing
```

If you run into any problems, you can set SELinux to permissive mode in its configuration file:

```
sudo sed -i 's|SELINUX=enforcing|SELINUX=permissive|g' /etc/selinux/config
```

Reboot and allow TFTP access:

```
sudo setsebool -P tftp_anon_write 1
sudo setsebool -P tftp_home_dir 1
```

FYI, disabling SELinux is not allowed and will prevent your system from booting.

## Steps

```
sudo yum -y install tftp tftp-server* 
sudo mkdir -p -m777 /var/lib/tftpboot
sudo chmod 777 /var/lib/tftpboot
sudo touch /var/lib/tftpboot/start.cfg
sudo chmod 777 /var/lib/tftpboot/start.cfg
sudo firewall-cmd --zone=public --add-service=tftp
sudo systemctl enable tftp
sudo systemctl start tftp
```

Development Notes:

```
R1>enable
R1#copy startup-config tftp://192.168.1.1/start.cfg
Address or name of remote host [192.168.1.1]? 
Destination filename [sc.cfg]? 
!!
402 bytes copied in 0.076 secs (5289 bytes/sec)
R1#copy startup-config tftp://192.168.1.10/start.cfg
Address or name of remote host [192.168.1.10]? 
Destination filename [sc.cfg]? 
!!
402 bytes copied in 0.076 secs (5289 bytes/sec)
R1#
R1#copy tftp://192.168.1.1/yo.txt flash:
Destination filename [yo.txt]? 
Accessing tftp://192.168.1.1/yo.txt...
Loading yo.txt from 192.168.1.1 (via FastEthernet0/0): !
[OK - 12 bytes]

12 bytes copied in 0.592 secs (20 bytes/sec)
R1#copy tftp://192.168.1.10/yi.txt flash:
Destination filename [yi.txt]? 
Accessing tftp://192.168.1.10/yi.txt...
Loading yi.txt from 192.168.1.10 (via FastEthernet0/0): !
[OK - 11 bytes]

11 bytes copied in 1.148 secs (10 bytes/sec)
R1#

R1#conf t
Enter configuration commands, one per line.  End with CNTL/Z.
R1(config)#ip tftp source-interface F0/0
R1(config)#end
R1#
```

Other stuff:

```
tftp 192.168.1.20 -m binary -c put localfile remotefile 
tftp 192.168.1.20 -m binary -c get remotefile localfile

IF NOT CONFIGURED/NO IP ADDRESS!!!
R1#copy startup-config tftp://192.168.1.10/start.cfg
Address or name of remote host [192.168.1.10]? 
Destination filename [start.cfg]? 
%Error opening tftp://192.168.1.10/start.cfg (Socket error)
R1#
```
