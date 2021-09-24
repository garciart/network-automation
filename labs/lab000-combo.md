# Adventures in Network Automation

## Lab 000 - Complete Automation Lab

This lab combines all the labs into a single, executable script.

***Notes:***

Before transferring files between the CentOS host and Cisco devices, you must install the following files on the host:

- ```xinetd``` - The Extended Internet Service Daemon (xinetd) listens for incoming requests over a network, using port numbers as identifiers, and launches the appropriate service for that request. For example, if xinetd hears a request over User Datagram Protocol (UDP) port 69, it will launch the Trivial File Transfer Protocol (TFTP) service. For more information, see [the Wikipedia entry for xinetd](https://en.wikipedia.org/wiki/Xinetd "xinetd").
- ```tftp``` and ```tftp-server``` - The Trivial File Transfer Protocol (TFTP) Client and Server is a simple file transfer protocol. Data transferred over UDP is not encrypted and is insecure. In addition, since TFTP uses the User Datagram Protocol (UDP), there are no transmission integrity checks, such as handshaking. However, TFTP is adequate for small file transfers, such transferring a configuration file between a host and a device over a dedicated line. For more information, see [the Wikipedia entry for TFTP](https://en.wikipedia.org/wiki/Trivial_File_Transfer_Protocol "TFTP") and [the Wikipedia entry for UDP](https://en.wikipedia.org/wiki/User_Datagram_Protocol "UDP").

```
sudo yum -y install xinetd*
sudo yum -y install tftp tftp-server* 
sudo mkdir -p -m777 /var/lib/tftpboot
sudo chmod 777 /var/lib/tftpboot
```

In addition, CentOS 7 runs Security-Enhanced Linux (SELinux) in enforcing mode by default, which prevents you from using insecure file transfer protocols, such as TFTP:

```
$ sestatus | grep "mode\|Mode"
Current mode:                   enforcing
Mode from config file:          enforcing
```

To use TFTP, you must set SELinux to permissive mode in its configuration file:

```
sudo sed -i 's|SELINUX=enforcing|SELINUX=permissive|g' /etc/selinux/config
```

Disabling SELinux is not allowed and will prevent your system from booting.

## Steps

**Part I:**
```
sudo yum -y install xinetd*
sudo yum -y install tftp tftp-server* 
sudo mkdir -p -m777 /var/lib/tftpboot
sudo chmod 777 /var/lib/tftpboot
sudo touch /var/lib/tftpboot/start.cfg
sudo chmod 777 /var/lib/tftpboot/start.cfg
sudo sed -i 's|SELINUX=enforcing|SELINUX=permissive|g' /etc/selinux/config
sudo reboot now
```

**Part II**
```
sudo setsebool -P tftp_anon_write 1
sudo setsebool -P tftp_home_dir 1
sudo firewall-cmd --zone=public --add-service=tftp
sudo systemctl enable tftp
sudo systemctl start tftp
```
