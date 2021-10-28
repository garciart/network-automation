# Adventures in Network Automation

## Lab 003 - Basic Network Device Security.

In this lab, you will secure a GNS3 device by preventing anonymous access

Start GNS3 by opening a terminal and inputting ```gns3_run```.

> **Note** - If you like, check out [https://docs.gns3.com/docs/using-gns3/beginners/the-gns3-gui](https://docs.gns3.com/docs/using-gns3/beginners/the-gns3-gui "The GNS3 GUI") to learn the different parts of the GNS3 Graphical User Interface (GUI).

Click on **File** ->  **New blank project**, or press  <kbd>Ctrl</kbd>+<kbd>N</kbd>, to create a new project. If GNS3 is
not running, make sure that you have set up your network bridge, and start GNS3 by inputting ```gns3``` in a Terminal (
the **Project** window should appear).

A pop-up dialog will appear, asking you to create a new project. Enter ```lab003``` in the ***Name*** textbox and click
the **OK** button.

![Project Dialog](../img/a10.png)

Complete the steps in [Lab 2 (Ping)](lab002-ping.md "Lab 2 (Ping)"), and Telnet back into the device by opening a Terminal and inputting the following
command. Using the instructions in [lab001-telnet](lab001-telnet "Lab 1 (Telnet)"), make sure your use the right console port:

```
telnet 192.168.1.1 5003
```

Enter ```show startup-config``` to see the device's start up configuration:

```
R1#show startup-config
!
version 12.4
service timestamps debug datetime msec
service timestamps log datetime msec
no service password-encryption
!
hostname R1
!
boot-start-marker
boot-end-marker
!
no aaa new-model
memory-size iomem 5
no ip icmp rate-limit unreachable
ip cef
!
no ip domain lookup
ip auth-proxy max-nodata-conns 3
ip admission max-nodata-conns 3
!
ip tcp synwait-time 5
!
interface FastEthernet0/0
 ip address 192.168.1.20 255.255.255.0
 duplex auto
 speed auto
!
interface FastEthernet0/1
 no ip address
 shutdown
 duplex auto
 speed auto
!
ip forward-protocol nd
!
no ip http server
no ip http secure-server
!
no cdp log mismatch duplex
!         
control-plane
!
line con 0
 exec-timeout 0 0
 privilege level 15
 logging synchronous
line aux 0
 exec-timeout 0 0
 privilege level 15
 logging synchronous
line vty 0 4
 login
!         
end
```

The exclamation points usually precede comments, but the Cisco command parser automatically includes them to make
configuration files more readable.

The configuration files hold a lot of good information, like the configuration of the device's ports. For example, at
the end of the configuration, there are three sections that begin with the work ```line```:

- ```line con 0``` is the configuration for the device's console port.
- ```line aux 0``` is the configuration for the device's auxiliary port.
- ```line vty 0 4``` is the configuration for the device's virtual teletype (vty) ports, which allow Telnet and Secure
  Shell (SSH) connections through Ethernet ports.

Notice that the virtual teletype (vty) ports require a login. However, the vty password is not configured. Let us set
some basic security, so we can access the device through the Ethernet ports and enter User EXEC mode; otherwise, you
will receive a ```Password required, but none set``` error.

```
R1#configure terminal ; Or 'conf t'
R1(config)#; Set cisco as the Privileged EXEC mode password (do not add comments to passwords)
R1(config)#enable password cisco
R1(config)#line console 0 ; Enter configuration mode for the console port
R1(config-line)#; Set cisco as the console terminal password (do not add comments to passwords)
R1(config-line)#password cisco
R1(config-line)#login ; Require console terminal login
R1(config-line)#end
R1#conf t
R1(config)#line aux 0 ; Enter configuration mode for the auxiliary port
R1(config-line)#; Set cisco as the auxiliary terminal password (do not add comments to passwords)
R1(config-line)#password cisco
R1(config-line)#login ; Require auxiliary terminal login
R1(config-line)#end
R1#conf t
R1(config)#line vty 0 4 ; Allow up to five connections for virtual teletype (vty) remote terminal access (Telnet, SSH, etc.)
R1(config-line)#; Set cisco as the remote terminal password (do not add comments to passwords)
R1(config-line)#password cisco
R1(config-line)#login ; Require Telnet and SSH login
R1(config-line)#end
R1#write memory ; Copy the modified running-config to the startup-config
```

Wait a few seconds for the messages to clear:

```
Building configuration...
[OK]
R1#
```

Re-enter ```show startup-config``` to see the device's new start up configuration:

```
!
version 12.4
service timestamps debug datetime msec
service timestamps log datetime msec
no service password-encryption
!
hostname R1
!
boot-start-marker
boot-end-marker
!
enable password cisco
!
no aaa new-model
memory-size iomem 5
no ip icmp rate-limit unreachable
ip cef
!
no ip domain lookup
ip auth-proxy max-nodata-conns 3
ip admission max-nodata-conns 3
!
ip tcp synwait-time 5
!
interface FastEthernet0/0
 ip address 192.168.1.20 255.255.255.0
 duplex auto
 speed auto
!
interface FastEthernet0/1
 no ip address
 shutdown
 duplex auto
 speed auto
!
ip forward-protocol nd
!
no ip http server
no ip http secure-server
!
no cdp log mismatch duplex
!
control-plane
!
line con 0
 exec-timeout 0 0
 privilege level 15
 password cisco
 logging synchronous
 login
line aux 0
 exec-timeout 0 0
 privilege level 15
 password cisco
 logging synchronous
 login
line vty 0 4
 password cisco
 login
!
end
```

Notice that the passwords are assigned, but in clear text. This is not very secure; let us fix that:

```
R1#configure terminal
R1(config)#; Encrypt the User EXEC mode password using an irreversible MD5 hash
R1(config)#enable password cisco
R1(config)#; Encrypt port passwords using a reversible Vigenere cipher
R1(config)#service password-encryption
R1(config)#end
R1#write memory ; Copy the modified running-config to the startup-config
```

Again, wait a few seconds for the messages to clear:

```
Building configuration...
[OK]
R1#
```

Re-enter ```show startup-config``` to see the device's start up configuration:

```
!
version 12.4
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname R1
!
boot-start-marker
boot-end-marker
!
enable password 7 00071A150754
!
no aaa new-model
memory-size iomem 5
no ip icmp rate-limit unreachable
ip cef
!
no ip domain lookup
ip auth-proxy max-nodata-conns 3
ip admission max-nodata-conns 3
!
ip tcp synwait-time 5
!
interface FastEthernet0/0
 ip address 192.168.1.20 255.255.255.0
 duplex auto
 speed auto
!
interface FastEthernet0/1
 no ip address
 shutdown
 duplex auto
 speed auto
!
ip forward-protocol nd
!
no ip http server
no ip http secure-server
!
no cdp log mismatch duplex
!
control-plane
!
line con 0
 exec-timeout 0 0
 privilege level 15
 password 7 02050D480809
 logging synchronous
 login
line aux 0
 exec-timeout 0 0
 privilege level 15
 password 7 0822455D0A16
 logging synchronous
 login
line vty 0 4
 password 7 0822455D0A16
 login
!
end
```

Notice that the passwords are now obscured.

Switch back to GNS3 and reload the device (you may have to stop and restart the device as well). This will also end your
Telnet session:

Attempt to Telnet back into the device. You will be prompted for a password; enter "cisco". If you try to enter User
EXEC Mode, you will once again be prompted for a password.

```
$ telnet 192.168.1.1 5003
Trying 192.168.1.1...
Connected to 192.168.1.1.
Escape character is '^]'.


User Access Verification

Password: 
R1>enable
Password:
R1#
```

End the Telnet session by pressing <kbd>Ctrl</kbd>+<kbd>]</kbd> and inputting "q". Now, reconnect to the device, but
through the FastEthernet0/1 port, using the IP address you assigned it earlier:

```
$ telnet 192.168.1.20
Trying 192.168.1.20...
Connected to 192.168.1.20.
Escape character is '^]'.


User Access Verification

Password: 
R1>enable
Password:
R1#
```

By the way, you can configure other options (do not set these at this time):

```
R1#configure terminal ; Or 'conf t'
R1(config)#hostname MyRouter ; Change the host name 
MyRouter(config)#no ip domain-lookup ; Require IP addresses instead of URLs to reduce typos
MyRouter(config)#line console 0
MyRouter(config-line)#exec-timeout 2 30 ; Timeout after 2 minutes and 30 seconds (default is 10)
MyRouter(config-line)#end
MyRouter#conf t
MyRouter(config)#hostname R1
MyRouter(config)#end
R1#
```

## The Code:

To recap, we:

1. Accessed the device through Telnet.
2. Entered Privileged EXEC Mode
3. ...
4. Closed the connection.

Like I stated earlier, this is easy to do for one device, but not for one hundred. Let us put these steps into a simple python script.

This is a bare-bones script that automates everything we did earlier. Lorem ipsum...

```
#!/usr/bin/python
"""Lab 003: Basic Network Device Security.
To run this lab:

* Start GNS3 by executing "gn3_run" in a Terminal window.
* Setup the lab environment according to lab003-security.md.
* Start all devices.
* Run this script (i.e., "Python lab003-security.py")
"""
from __future__ import print_function

import sys
import time

import pexpect

print("Connecting to the device...")

# Connect to the device and allow time for any boot messages to clear
child = pexpect.spawn("telnet 192.168.1.1 5001")
time.sleep(10)
child.sendline("\r")

# Check for a prompt, either R1> (User EXEC mode) or R1# (Privileged EXEC Mode)
# and enable Privileged EXEC Mode if in User EXEC mode.
index = child.expect_exact(["R1>", "R1#", ])
if index == 0:
    child.sendline("enable\r")
    child.expect_exact("R1#")
# Enter Privileged EXEC mode
child.sendline("configure terminal\r")
child.expect_exact("R1(config)#")
# Set cisco as the User EXEC mode password
child.sendline("enable secret cisco\r")
child.expect_exact("R1(config)#")
# Enter line configuration mode and specify the type of line
child.sendline("line console 0\r")
child.expect_exact("R1(config-line)#")
# Set cisco as the console terminal line password
child.sendline("password cisco\r")
child.expect_exact("R1(config-line)#")
# Require console terminal login
child.sendline("login\r")
child.expect_exact("R1(config-line)#")
# Allow up to five connections for virtual teletype (vty) remote console access (Telnet, SSH, etc.)
child.sendline("line vty 0 4\r")
child.expect_exact("R1(config-line)#")
# Set cisco as the remote console access password
child.sendline("password cisco\r")
child.expect_exact("R1(config-line)#")
# Require Telnet and SSH login
child.sendline("login\r")
child.expect_exact("R1(config-line)#")
child.sendline("end\r")
child.expect_exact("R1#")
# Save the configuration
child.sendline("write memory\r")
"""
Building configuration...
[OK]
R1#
"""
child.expect_exact("[OK]", timeout=120)
# Set the new configuration as default
child.sendline("copy running-config startup-config\r")
child.expect_exact("Destination filename [startup-config]?")
child.sendline("\r")
"""
Building configuration...
[OK]
R1#
"""
child.expect_exact("[OK]", timeout=120)
print("Configuration successful.")

print("Checking security...")
child = pexpect.spawn("telnet 192.168.1.20")
child.sendline("cisco\r")
child.expect_exact("R1>")
print("Security is good.")

# Close Telnet and disconnect from device
child.sendcontrol("]")
child.sendline('q\r')
print("Successfully configured the device and checked connectivity.")
```

Run the script, and you will get the following output:

```
$ python lab003-security.py

Hello, friend.

Script complete. Have a nice day.
```

**Congratulations!** You have secured a device using Python!