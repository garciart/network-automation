# Welcome to the Labs!

![All Devices Started](../../img/adventures-automation.gif)

The labs in this folder will show you how to automate simple network tasks using Python. However, before starting the labs, run these commands through the Cisco command-line interface (CLI), as you would do with a real network device. This will give you an idea of what to look for and what to expect from each lab.

>**NOTE - This tutorial is primarily for Python programmers who are learning about network engineering. If you are a network engineer or know basic Cisco CLI commands, you can skip this tutorial and go the first lab.**

- [Set up the Host's Linux Environment](#set-up-the-hosts-linux-environment "Set up the Host's Linux Environment")
- [Access a network device's Privileged EXEC Mode](#access-a-network-devices-privileged-exec-mode "Access a network device's Privileged EXEC Mode")
- [Format a network device's flash memory](#format-a-network-devices-flash-memory "Format a network device's flash memory")
- [Get information about a network device](#get-information-about-a-network-device "Get information about a network device")
- [Enable Layer 3 communications to and from a network device](#enable-layer-3-communications-to-and-from-a-network-device "Enable Layer 3 communications to and from a network device")
- [Secure a network device](#secure-a-network-device "Secure a network device")
- [Set a network device's clock](#set-a-network-devices-clock "Set a network device's clock")
- [Transfer files to and from a network device](#transfer-files-to-and-from-a-network-device "Transfer files to and from a network device")
- [Securely connect to a network device](#securely-connect-to-a-network-device "Securely connect to a network device")
- [Securely transfer files to and from a network device](#securely-transfer-files-to-and-from-a-network-device "Securely transfer files to and from a network device") 
- [Shutdown](#shutdown "Shutdown")

---
## Set up the Host's Linux Environment 

First, ensure you have installed and started GNS3 per the instructions in the [Adventures in Automation](../../README.md "Adventures in Automation") tutorial. We recommend you follow our suggestion in the post-script to open a Linux Terminal and start GNS3 by entering ```gns3_run```. For this tutorial, you will continue to use the Automation project in the [Adventures in Automation](../../README.md "Adventures in Automation") tutorial.

>**NOTE** - By the way, you will also continue to use the Cisco 3745 Multi-Service Access Router for the labs, so no further configuration is needed. All you will have to do from the GNS3 GUI is start the device; occasionally get some info or reload the device; and stop the device before exiting. 

Second, make sure the clients and services required for the labs exist and are enabled on the host (they should have been installed during the [Adventures in Automation](../../README.md "Adventures in Automation") tutorial):

1. **Teletype Network (Telnet) Client** - Telnet is a protocol that allows devices to communicate over a network. It uses the Transmission Control Protocol (TCP) to ensure a reliable session, but it neither authenticates users nor encrypts any data transmitted, so it is not secure. You will use Telnet to configure the device to switch to the Secure Shell (SSH) Protocol.
2. **Network Time Protocol (NTP) Service** - Some network devices may not have a battery-supported system clock, which means that they do not retain the correct time and date after they are powered off, reloaded, or restarted. However, several tasks, such as logging or synchronization, depend on an up-to-date clock. You will use NTP to update the device's clock using the host's clock.
3. **Trivial File Transfer Protocol (TFTP) Service** - TFTP is a very simple file transfer service. It uses User Datagram Protocol (UDP) and no encryption, so it is neither reliable for large file transfers nor secure. However, it is good for transferring small files over direct connections, such as through a Console or Auxiliary port. You will use TFTP to transfer configuration files between the device and the host.
4. **Very Secure FTP Daemon (vsftpd) Service** - vsftpd is a version of the File Transfer Protocol (FTP) service, used by many Linux systems. It uses the Transmission Control Protocol (TCP) to ensure a reliable session, and it authenticates users before transferring files. However, FTP does not encrypt data out-of-the-box, but it can be customized to use Secure Sockets Layer (SSL), Transport Layer Security (TLS), etc. You will use FTP to transfer files between the device and the host, once you have secured the device.
5. **Secure Shell (SSH) Protocol Service** - SSH allows secure communications between devices over an unsecure network. It uses the Transmission Control Protocol (TCP) to ensure a reliable session. SSH uses public key cryptography to authenticate users and an industry-approved cipher to encrypt any data transmitted. You will use SSH to run commands on the device, once you have generated the required cryptographic keys on the device.
6. **Secure Copy Protocol (SCP) Program** - SCP is a file transfer program that uses the Secure Shell (SSH) Protocol to securely transfer files between devices. It uses the Transmission Control Protocol (TCP) to ensure a reliable session, and relies on SSH for authentication and encryption. SCP is deprecated, though, and its creators recommend you use the Secure File Transfer Protocol (SFTP) or rsync. However, older Cisco Internetwork Operating Systems (IOS) cannot use either alternative, so you will use SCP to transfer files when using SSH.

Check the status of the Telnet and SCP programs by entering the following commands:

```
which telnet
which scp
```

After a few seconds, you will see the following output:

```
[gns3user@localhost ~]$ which telnet
/usr/bin/telnet
[gns3user@localhost ~]$ which scp
/usr/bin/scp
```

>**NOTE** - If you see ```/usr/bin/which: no telnet``` or ```/usr/bin/which: no scp```, the program is not installed or loaded. Make sure you installed GNS3 per the instructions in the [Adventures in Automation](../../README.md "Adventures in Automation") tutorial.

Check the status of the services by entering the following commands:

```
systemctl status ntpd
systemctl status tftp
systemctl status vsftpd
systemctl status sshd
```

After a few seconds, you will see the following output:

```
[gns3user@localhost ~]$ systemctl status ntpd
● ntpd.service - Network Time Service
   Loaded: loaded (/usr/lib/systemd/system/ntpd.service; disabled; vendor preset: disabled)
   Active: inactive (dead)

[gns3user@localhost ~]$ systemctl status tftp
● tftp.service - Tftp Server
   Loaded: loaded (/usr/lib/systemd/system/tftp.service; indirect; vendor preset: disabled)
   Active: inactive (dead)
     Docs: man:in.tftpd

[gns3user@localhost ~]$ systemctl status vsftpd
● vsftpd.service - Vsftpd ftp daemon
   Loaded: loaded (/usr/lib/systemd/system/vsftpd.service; disabled; vendor preset: disabled)
   Active: inactive (dead)

[gns3user@localhost ~]$ systemctl status sshd
● sshd.service - OpenSSH server daemon
   Loaded: loaded (/usr/lib/systemd/system/sshd.service; enabled; vendor preset: enabled)
   Active: active (running) since Sun 2021-11-14 11:46:57 EST; 2h 4min ago
     Docs: man:sshd(8)
           man:sshd_config(5)
 Main PID: 1253 (sshd)
    Tasks: 1
   CGroup: /system.slice/sshd.service
           └─1253 /usr/sbin/sshd -D

[gns3user@localhost ~]$ 
```

You see that ntpd, tftp, and vsftpd are present, but disabled, while the sshd service is running.

>**NOTE** - If you see ```Unit (ntpd, tftp, vsftpd, or sshd).service could not be found.```, the services are not installed or loaded. Make sure you installed GNS3 per the instructions in the [Adventures in Automation](../../README.md "Adventures in Automation") tutorial.

Change your firewall settings by entering the following commands. If prompted, enter your sudo password:

```
sudo firewall-cmd --zone=public --add-port=20/tcp
sudo firewall-cmd --zone=public --add-port=21/tcp
sudo firewall-cmd --zone=public --add-port=22/tcp
sudo firewall-cmd --zone=public --add-service=ftp
sudo firewall-cmd --zone=public --add-port=23/tcp
sudo firewall-cmd --zone=public --add-port=123/udp
sudo firewall-cmd --zone=public --add-service=ntp
sudo firewall-cmd --zone=public --add-port=69/udp
sudo firewall-cmd --zone=public --add-service=tftp
```

The first three commands allow FTP client and server communications through ports 20 and 21. The next command opens port 22 for secure communications. The following command allows Telnet client communications through port 23. The next two commands permit NTP traffic, allowing the host to act as an NTP server. The final two commands allow TFTP client and server communications through port 69.

>**NOTE** - SSH is already running, so if you run the following command...
> 
>```sudo firewall-cmd --zone=public --add-service=ssh```
> 
>...you will get the following response:
>
>```
>Warning: ALREADY_ENABLED: 'ssh' already in 'public'
>success
>```
> 
>However, you can run this command if you like; it will not affect the system.

>**NOTE** - If you run into any errors, make sure you installed GNS3 per the instructions in the [Adventures in Automation](../../README.md "Adventures in Automation") tutorial.
>- Do not reload the firewall daemon. For security purposes, these changes are temporary and the ports will close if the system crashes or reboots.
>- Do not install a Telnet service. You will only need the Telnet client, which you installed during the GNS3 setup. 

To enable the NTP service, you may need to make some modifications to the host system. First, check if the host is configured as an NTP server by looking for the reserved NTP server address:

```grep "server 127.127.1.0" /etc/ntp.conf```

You should see the search string, ```server 127.127.1.0```, repeated back in red. If nothing appears, it means that the NTP server is not active. Append the local server information to the NTP configuration file, using the following command:

```echo -e "server 127.127.1.0" | sudo tee -a /etc/ntp.conf```

Finally, start the NTP service:

```sudo systemctl start ntpd```

Before you enable the TFTP service, create the TFTP default directory (if it does not exist) and give it the necessary permissions to accept and send files:

```
sudo mkdir --parents --verbose /var/lib/tftpboot 
sudo chmod 777 --verbose /var/lib/tftpboot
```

For many reasons, TFTP is very limited. TFTP can only copy to an ***existing*** file; it cannot ***create*** a new copy. Therefore, create a shell file for TFTP to copy data into, and give the shell the necessary permissions to accept the data:

```
sudo touch /var/lib/tftpboot/startup-config.bak
sudo chmod 777 --verbose /var/lib/tftpboot/startup-config.bak
```

Finally, start the TFTP service:

```sudo systemctl start tftp```

To enable the FTP service, you may need to make some modifications to the host system. First, check if an FTP user is listed in the vsftpd configuration file:

```sudo grep "ftp_username=" /etc/vsftpd/vsftpd.conf```

You should see the search string, ```ftp_username=nobody```, repeated back in red. If nothing appears, it means that an FTP user is listed. Append the default user to the FTP configuration file, using the following command:

```echo -e "ftp_username=nobody" | sudo tee -a /etc/vsftpd/vsftpd.conf```

Finally, start the FTP service:

```sudo systemctl start vsftpd```

>**NOTE** - The SSH service is already running, but if you want to run the following command, it will not affect the system:
> 
>```sudo systemctl start sshd```

---
## Access a network device's Privileged EXEC Mode

Now that you have set up the host system, you can run the commands in a Console port session. First, get the gateway IP address and Console port's number from the **Topology Summary** in the top left-hand corner.:

![Topology Summary](../../img/a32.png)

If the Console port number is difficult to see, you can get the information by expanding the dock or right-clicking on the R1 node and selecting **Show node information**:

![Show Node Information](../../img/a35.png)

![Node Information](../../img/a36.png)

Connect to the device using Telnet. In your case, the Console port number is ```5001```:

```telnet 192.168.1.1 5001```

Not to be overly dramatic, but after you input that command, ***STOP!*** You may scroll, but do not press <kbd>Enter</kbd> or input any more commands yet.

You will see messages from the startup sequence of the device appear on the screen:

```
SETUP: new interface FastEthernet0/0 placed in "shutdown" state
SETUP: new interface FastEthernet0/1 placed in "shutdown" state

Press RETURN to get started!

sslinit fn

*Mar  1 00:00:03.871: %LINEPROTO-5-UPDOWN: Line protocol on Interface VoIP-Null0, changed state to up
*Mar  1 00:00:03.927: %SYS-5-CONFIG_I: Configured from memory by console
*Mar  1 00:00:04.087: %SYS-5-RESTART: System restarted --
```

For you, the most important message is:

```Press RETURN to get started!```

If the device reloaded correctly, this line will appear near the end of the boot sequence. However, you should see no prompts (e.g., ```R1>```, ```R1#```, etc.). If you see any prompts, especially a prompt followed by a command (e.g., "```R1#configure terminal```", etc.), that means that the device was not properly reloaded, and you may be using someone else's virtual teletype (VTY) session. This is dangerous for many reasons, since you may be eavesdropping on another user's session or creating a race condition by simultaneously entering commands at the same time as another user.

>**NOTE** - Unfortunately, entering the ```reload``` command in GNS3 will cause the Console terminal to "hang", so if you do see a prompt, exit Telnet by pressing <kbd>Ctrl</kbd>+<kbd>]</kbd>, and inputting <kbd>q</kbd>. Once you have exited Telnet, go to the GNS3 GUI and reload the device:
>
>![Reload the Device](../../img/b01.png)

If you do not see a prompt, press <kbd>Enter</kbd> now. 

>**NOTE** - If the following text appears after you press <kbd>Enter</kbd>...
>
>```
>User Access Verification
>
>Password: 
>```
>
>...it means that the device has already been configured by someone else. There is nothing wrong with that, and, as long as you have permission and the proper credentials, you can automate tasks for the device. However, for your labs, you need to use an unconfigured device.
>
>Unfortunately, there is no easy way to reset the device to its factory settings in GNS3; you will have to delete the device in the GNS3 workspace, and replace it with a new device.
>
>***If this is the first time you are using GNS3, other than in the [Adventures in Automation](../../README.md "Adventures in Automation") tutorial, you should not run into an improperly reloaded device, an open virtual teletype session, or a previously configured device. We only cover these potentially dangerous situations to allow you to recognize them in real life, when configuring an actual device for Layer 3 communications.***

If you are greeted with a simple ```R1#```, you are good to go. You are in **Privileged EXEC Mode**, the default startup mode for Cisco devices in GNS3.

>**NOTE** - A real, brand-new device would not boot into **Privileged EXEC Mode**, but would prompt you for one of the following:
> 
>```Would you like to terminate autoinstall? [yes]:```
>
>or
> 
>```Would you like to enter the initial configuration dialog? [yes/no]:```
> 
>However, GNS3 devices are not real devices, so the first prompt you should see is the **Privileged EXEC Mode** prompt. Some devices may display a ```Router>``` prompt instead. This means you are in **User EXEC Mode**, an interface that allows limited configuration and interaction with the device. Enter the following commands to reach **Privileged EXEC Mode** and set the correct host name:
>
>```
>enable ; Enter Privileged EXEC Mode
>configure terminal ; Enter Global Configuration Mode
>hostname R1 ; Change the device hostname
>end ; Return to Privileged EXEC Mode
>write memory ; Save the changes to the default configuration
>```
> 
>I will go over these commands in more detail later on. 

---
## Format a network device's flash memory

The first thing you want to do is to format the device's built-in CompactFlash (CF) memory card. If you scroll through the startup output, you may see the following status message:

```*Mar  1 00:00:04.135: %PCMCIAFS-5-DIBERR: PCMCIA disk 0 is formatted from a different router or PC. A format in this router is required before an image can be booted from this device```

The Cisco 3745's PCMCIA disk 0, known as ```flash:```, is used to store the system image, configuration files, and more. While you can take a chance and hope the memory card works this device, it is better to format it before configuring the device. Therefore, enter the following command:

```format flash:```

You will be prompted twice to confirm. Press <kbd>Enter</kbd> each time:

```
Format operation may take a while. Continue? [confirm]
Format operation will destroy all data in "flash:".  Continue? [confirm]
```

If the device's memory and disks were configured correctly in [Adventures in Automation](../../README.md "Adventures in Automation"), you should see the following output:

```
Format: Drive communication & 1st Sector Write OK...
Writing Monlib sectors.
.........................................................................................................................
Monlib write complete 
..
Format: All system sectors written. OK...

Format: Total sectors in formatted partition: 130911
Format: Total bytes in formatted partition: 67026432
Format: Operation completed successfully.

Format of flash complete
R1#
```

The command ```show flash:``` will display the contents of CF memory card:

```
No files on device
66875392 bytes available (0 bytes used)
R1#
```

---
## Get information about a network device

Now, there are times you will need to get the device's Internetwork Operating System (IOS) version, the device's serial number, etc. Enter the following commands to get that information:

```
show inventory | include [Cc]hassis
show version | include [Pp]rocessor [Bb]oard [IDid]
show version | include [IOSios] [Ss]oftware
```

Note the ```[Cc]```, ```[Pp]```, etc., used by the include statements. You can filter output using regular expressions in the Cisco CLI.

After entering the commands, you should see the following output after each command:

```
R1#show inventory | include [Cc]hassis
NAME: "3745 chassis", DESCR: "3745 chassis"
R1#show version | include [Pp]rocessor [Bb]oard [IDid]
Processor board ID FTX0945W0MY
R1#show version | include [IOSios] [Ss]oftware
Cisco IOS Software, 3700 Software (C3745-ADVENTERPRISEK9-M), Version 12.4(25d), RELEASE SOFTWARE (fc1)
R1#
```

You are using a 3745 Router, serial number FTX0945W0MY, running Cisco's Advanced Enterprise Services IOS version 12.4(25d).

---
## Enable Layer 3 communications to and from a network device

Next, you will enable Layer 3 connectivity by assigning an IP address to the device. Right now, in GNS3, you are simulating a direct connection from the host to the device through the Console port. However, the Console port is not designed to be accessed remotely. Our goal is to automate tasks, such as IOS updates and reconfigurations, and perform them remotely. The best option is to use a secure shell (SSH) to connect to the device over the network, and, to use SSH, the device must have an IP address. Follow these steps:

|Task|Input|Output|
|---|---|---|
|1. Get the IP interfaces for the device|```show ip interface brief```|```Interface........IP-Address....OK?..Method..Status.................Protocol```<br />```FastEthernet0/0..unassigned....YES..NVRAM...administratively.down..down```<br />```FastEthernet0/1..unassigned....YES..NVRAM...administratively.down..down```<br />```R1#```|
|2. Enter **Global Configuration Mode**|```configure terminal```|```Enter configuration commands, one per line.  End with CNTL/Z.```<br />```R1(config)#```|
|3. Enter **Interface Configuration Mode** for FastEthernet0/1|```interface FastEthernet0/0```|```R1(config-if)#```|
|4. Assign an IP address|```ip address 192.168.1.20 255.255.255.0```|```R1(config-if)#```|
|5. Open the interface|```no shutdown```|```*Mar  1 00:49:04.939: %LINK-3-UPDOWN: Interface FastEthernet0/0, changed state to up```<br />```*Mar  1 00:49:05.939: %LINEPROTO-5-UPDOWN: Line protocol on Interface FastEthernet0/0, changed state to up```<br />```R1(config-if)#```|
|6. Return to **Privileged EXEC mode**|```end```|```*Mar  1 00:51:16.071: %SYS-5-CONFIG_I: Configured from console by console```<br />```R1#```|
|7. Check the status of the IP interfaces|```show ip interface brief```|```Interface........IP-Address....OK?..Method..Status.................Protocol```<br />```FastEthernet0/0..192.168.1.20..YES..manual..up.....................up```<br />```FastEthernet0/1..unassigned....YES..NVRAM...administratively.down..down```<br />```R1#```|

To make sure that everything is connected, ping the host from the device:

```
ping 192.168.1.10
```

After a few seconds, you will see the following output:

```
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 192.168.1.10, timeout is 2 seconds:
.!!!!
Success rate is 80 percent (4/5), round-trip min/avg/max = 4/31/48 ms
R1#
```

>If you see ```Success rate is 0 percent (0/5)```, go back to the GNS3 GUI and make sure you are connected. If so, but you are still at 0 percent, open another Linux Terminal and enter the following command:
>
>```ip address show | grep '[0-9]: e[mnt]'```
>
>Note the name of the isolated interface from the [Adventures in Automation](../../README.md "Adventures in Automation") tutorial (e.g., ```enp0s8```, etc.):
>
>```
>2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
>3: enp0s8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast master br0 state UP group default qlen 1000
>```
>
>Reapply an IP address to the interface:
>
>```sudo ip address replace 192.168.1.10/24 dev enp0s8```
>
>Go back to the Telnet terminal and attempt to ping the host from the device again. If the success rate is still zero, go back and review the steps in the [Adventures in Automation](../../README.md "Adventures in Automation") tutorial.

Before continuing, make that change to the interface permanent by updating the device's **startup configuration**; otherwise, the device will shutdown the interface after each reload or reboot:

```write memory```

After a few seconds, you will see the following output:

```
Building configuration...
[OK]
R1#
```

>**NOTE** - Most Cisco devices have two configuration files:
>1. **running-configuration** - This file keeps track of all changes to the device's configuration for the current session. It is held in the device's RAM (```system:```), and the file, along with any changes, are discarded when the device is turned off or reloaded, unless saved to the startup-configuration file. 
>2. **startup-configuration** - This file is stored in the device's nonvolatile random-access memory (```nvram:```) and is read by the device upon startup. Any changes to the device's configuration must be saved to this file to become permanent. 

---
## Secure a network device

Exit Telnet by pressing <kbd>Ctrl</kbd>+<kbd>]</kbd>, and inputting <kbd>q</kbd>. Once you have exited Telnet, go to the GNS3 GUI and reload the device:

![Reload the Device](../../img/b01.png)

Go back to the Linux Terminal and attempt to Telnet into the device using the IP address:

```telnet 192.168.1.20```

After a few seconds, you will see the following output:

```
Trying 192.168.1.20...
Connected to 192.168.1.20.
Escape character is '^]'.

Password required, but none set
Connection closed by foreign host.
```

![What???](../../img/whaat-huh.gif "What???")

What happened? Well, when you made your changes permanent, the current running configuration added this line to the end of the device's startup configuration, stored in the device's nonvolatile random-access memory (NVRAM):

```
line vty 0 4
 login
```

The Cisco 3745 has five virtual teletype (VTY) lines (0 through 5). As a fail-safe, the device requires a login whenever a user attempts to access it through a VTY line, as you just attempted to do. The problem is that you never set a password for the VTY line, so the device cannot let you in. 

You have several options. 

1. One way is to continue directly connecting to the Console port, but, as we stated earlier, our goal is to automate tasks, such as IOS updates and reconfigurations, and perform them remotely. In addition, imagine you had to update each router in each cabinet for a data center with 100+ cabinets; it would take a long time. 
2. Another way is to change the configuration, by replacing ```login``` with ```no login```, removing the authentication requirement.
3. However, the best option is to secure the lines; whenever you can, "err" on the side of security.

So, in the Linux Terminal, Telnet back into the device through the Console port:

```telnet 192.168.1.1 5001```

Now you will secure the VTY line. Set the username to ```admin```, the privilege level to "15", and the password to ```cisco```:

>**NOTE** - Cisco devices have 16 privilege levels (0 through 15). 13 are customizable, while three are set by the IOS:
> 
>- 0 - No privileges
>- 1 - Read-only and access to the ping command
>- 15 - Full access, including reading and writing configuration files
> 
>To see your privilege level, enter ```show privilege``` at the prompt.

```
configure terminal ; Enter Global Configuration Mode
; Secure the VTY lines and return to Global Configuration Mode
username admin privilege 15 password cisco
line vty 0 4 ; Enter Line Configuration Mode for VTY
login local ; See the note below
exit
```

>**NOTE** - Since you identified a user (```username admin```), you must require a ```local``` username when logging in remotely. If you do not use a username (e.g., ```privilege 15 password cisco```), just use require a ```login``` password. 

As a matter of fact, you might as well secure access to the Console port line, the Auxiliary port line, and Privileged EXEC Mode:

```
line console 0 ; Enter Line Configuration Mode for the Console port
password ciscon
login  ; Secure the Console port
exit ; Return to Global Configuration Mode
line aux 0 ; Enter Line Configuration Mode for the Auxiliary port
password cisaux
login ; Secure the Auxiliary port
exit ; Return to Global Configuration Mode
enable password cisen
end ; Secure and return to Privileged EXEC Mode
write memory ; Update the startup-configuration
```

>**NOTE:** 
>- In real life, make sure you use better passwords.
>- The maximum length for a Cisco password is **64** characters.
>- Never add comments after a Cisco password; they will be included in the password.
>- Check out [xkcd's take on passwords](https://xkcd.com/936/ "xkcd:Password Strength").

To test your security, exit **Privileged EXEC Mode**:

```disable```

You are greeted with the **User EXEC Mode** prompt:

```R1>```

Attempt to re-enter **Privileged EXEC Mode**:

```enable```

When prompted for a password, enter the password for **Privileged EXEC Mode** (i.e., ```cisen```). You should see the **Privileged EXEC Mode** prompt:

```R1#```

>**NOTE** - If something went wrong, attempt to reconfigure the passwords again. However, if you are stuck in **User EXEC Mode**, you will have to delete the device in the GNS3 workspace, and replace it with a new device.

Before you go on, take a look at the startup configuration file:

```show startup-config```

You should see something similar to the following output:

```
Using 1017 out of 155640 bytes
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
enable password cisen
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
username admin password 0 cisco
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
 password ciscon
 logging synchronous
 login
line aux 0
 exec-timeout 0 0
 privilege level 15
 password cisaux
 logging synchronous
 login
line vty 0 4
 login local
!
end
```

>**NOTE** - Don't worry about the exclamation points; they usually precede comments, and the Cisco command parser automatically includes them to make configuration files more readable.

There's a lot of good information in this file, but what is worrisome is the fact that we are not employing encryption and the passwords are all in plain text!

```
no service password-encryption

enable password cisen

username admin password 0 cisco

line con 0
 password ciscon

line aux 0
 password cisaux
```

Fix the **Privileged EXEC Mode** password first by removing the plain text and replacing it with a hashed password:

>**NOTE** - Cisco uses its own MD5 hash algorithm with a salt, resulting in a 30-character string.

```
configure terminal
no enable password
enable secret cisen
end
write memory
```

Next, fix the VTY password by removing the plain text and replacing it with a hashed password:

```
configure terminal
no username admin password cisco
username admin privilege 15 secret cisco
end
write memory
```

Finally, obscure the Console port and Auxiliary port passwords by enabling the password encryption service:

>**NOTE** - Cisco uses a reversible Vigenère cipher, not a hashing algorithm, for its password encryption service, resulting in a 14-character alphanumeric string.

```
configure terminal
service password-encryption
end
write memory
```

Take another look at the startup configuration file:

```show startup-config```

You should see changes similar to the following:

```
service password-encryption

enable secret 5 $1$GTon$HkSl2mJ3D8OB3lvCgNzK.0

username admin privilege 15 secret 5 $1$B2kV$6zQIQSPqM05TZzHh4NCPx1

line con 0
 password 7 05080F1C224340

line aux 0
 password 7 121A0C04131E14
```

Exit Telnet by pressing <kbd>Ctrl</kbd>+<kbd>]</kbd>, and inputting <kbd>q</kbd>. Once you have exited Telnet, go to the GNS3 GUI and reload the device:

![Reload the Device](../../img/b01.png)

Go back to the Linux Terminal and attempt to Telnet into the device using the IP address:

```telnet 192.168.1.20```

After a few seconds, you will see the following output:

```
Trying 192.168.1.20...
Connected to 192.168.1.20.
Escape character is '^]'.

User Access Verification

Username: admin
Password: 
R1#
```

---
## Set a network device's clock

Next, you will set the device's clock. As we stated earlier, this is a simple, but very important, task, since tasks, such as logging or synchronization, depend on an up-to-date clock. To this manually, enter the following command:

```clock set 12:00:00 Jan 1 2021```

After a few seconds, you will see the following output:

```
*Jan  1 12:00:00.000: %SYS-6-CLOCKUPDATE: System clock has been updated from 00:24:57 UTC Fri Mar 1 2002 to 12:00:00 UTC Fri Jan 1 2021, configured from console by console.
R1#
```

Unfortunately, our device may not retain manual clock settings after it is powered down. Luckily, you activated an NTP service on the host; now that you have Layer 3 connectivity, the device can use the host to update its clock. Do this by entering the following commands:

```
configure terminal
ntp server 192.168.1.10
end
```

Wait a few seconds for the NTP service to connect, and enter the following commands:

```
show ntp status
show clock
```

After a few seconds, you will see the following output:

```
R1#show ntp status
Clock is synchronized, stratum 4, reference is 192.168.1.10
nominal freq is 250.0000 Hz, actual freq is 250.0000 Hz, precision is 2**18
reference time is E533F0F5.2A9B4330 (18:54:45.166 UTC Mon Nov 8 2021)
clock offset is -20.6188 msec, root delay is 33.42 msec
root dispersion is 193.48 msec, peer dispersion is 132.17 msec
R1#show clock     
18:54:50.577 UTC Mon Nov 8 2021
```

Your devices clock should match your system clock, offset for Coordinated Universal Time (UTC). If you update the startup-configuration, the device will always check the host's IP address for an NTP server:

```write memory```

---
## Transfer files to and from a network device

>**NOTE** - You are now using Layer 3 communications, not a direct console line. As in real life, your connection may time out more often. Before sending commands in the blind, as you will do when automating tasks using Python, always check you are connected first. 

If you made it this far, congratulations!

At the beginning of this tutorial, you started a TFTP service on the host. Now that you have Layer 3 connectivity, you will use it to back up and save the startup configuration.  

Enter the following commands:

```
configure terminal
ip tftp source-interface FastEthernet0/0
end
write memory
```

This tells the device to use the FastEthernet port 0/0 for all TFTP transfers.

Next, transfer the file from the device to the host:

```copy nvram:/startup-config tftp://192.168.1.10/startup-config.bak```

You may be prompted to confirm the remote host's IP address and destination filename. You've already provided that information; press <kbd>Enter</kbd> each time:

```
Address or name of remote host [192.168.1.10]? 
Destination filename [startup-config.bak]? 
!!
1311 bytes copied in 0.104 secs (12606 bytes/sec)
R1#
```

If you open another Linux Terminal and enter the following command, you will see the backup file and its contents:

```
ll /var/lib/tftpboot
cat /var/lib/tftpboot/startup-config.bak
```

Go back to the Telnet terminal. Just in case you lose access to the host, back up the backup file to the device's flash memory:

```copy tftp://192.168.1.10/startup-config.bak flash:/startup-config.bak```

You will be prompted to confirm the destination filename. You've already provided that information; press <kbd>Enter</kbd>:

```
Destination filename [startup-config.bak]? 
Accessing tftp://192.168.1.10/startup-config.bak...
Loading startup-config.bak from 192.168.1.10 (via FastEthernet0/0): !
[OK - 1311 bytes]

1311 bytes copied in 0.216 secs (6069 bytes/sec)
R1#
```

Use the following commands to see the backup of the backup file and its contents:

```
show flash:
more flash:/startup-config.bak
```

After a few seconds, you will see the following output. By the way, press <kbd>Space</kbd> to continue at the ```--More--``` prompt:

```
R1#show flash:
-#- --length-- -----date/time------ path
1         1311 Nov 8 2021 18:58:00 +00:00 startup-config.bak

66871296 bytes available (4096 bytes used)

R1#more flash:/startup-config.bak
!
! Last configuration change at 18:57:10 UTC Mon Nov 8 2021 by admin
! NVRAM config last updated at 18:57:12 UTC Mon Nov 8 2021 by admin

...

ntp clock-period 17179856
ntp server 192.168.1.10
!
end
```

>**NOTE** - If you want to disable the ```--More--``` prompt, enter the command ```terminal length 0``` before showing the file.

If anything goes wrong with the transfer, enter the following commands:

```
debug tftp packets
debug tftp events
```

You will receive verbose feedback about the transfer, allowing you to debug any problems.

Now, you will once again back up the startup-configuration, this time using the more secure and reliable FTP service. 

When transferring a file using FTP, you must supply the recipient's username and password. In addition, FTP will save the file in the recipient's home folder, preventing you from overwriting a system file or other sensitive data.

>**NOTE** - If you attempt to send the file to /var/lib/tftpboot on a Security-Enhanced Linux (SELinux) enabled host, SELinux will stop the transfer, stating "Permission denied", regardless if the directory has full read-write-execute (777) permissions. You will have to modify SELinux, which is out of the scope of this basic tutorial.

Enter the following commands:

```
configure terminal
ip ftp source-interface FastEthernet0/0
end
write memory
```

This tells the device to use the FastEthernet port 0/0 for all FTP transfers.

Next, transfer the file from the device to the host:

```copy nvram:/startup-config ftp://gns3user:gns3user@192.168.1.10/startup-config.ftp```

You will be prompted to confirm the remote host's IP address and destination filename. You've already provided that information; press <kbd>Enter</kbd> each time:

```
Address or name of remote host [192.168.1.10]? 
Destination filename [startup-config.ftp]? 
Writing startup-config.ftp !
1351 bytes copied in 0.248 secs (5448 bytes/sec)
R1#
```

If you open another Linux Terminal and enter the following command, you will see the backup file and its contents:

```
ll /home/gns3user
cat /home/gns3user/startup-config.ftp
```

Go back to the Telnet terminal. Transfer the file from the host back to the device:

```copy ftp://gns3user:gns3user@192.168.1.10/startup-config.ftp flash:/startup-config.ftp```

You will be prompted to confirm the remote host's IP address and destination filename. You've already provided that information; press <kbd>Enter</kbd> each time:

```
Destination filename [startup-config.ftp]? 
Accessing ftp://gns3user:gns3user@192.168.1.10/startup-config.ftp...
Loading startup-config.ftp !
[OK - 1351/4096 bytes]

1351 bytes copied in 0.508 secs (2659 bytes/sec)
R1#
```

Use the following commands to see the uploaded file and its contents:

```
show flash:
more flash:/startup-config.ftp
```

After a few seconds, you will see the following output. By the way, press <kbd>Space</kbd> to continue at the ```--More--``` prompt:

```
R1#show flash:
-#- --length-- -----date/time------ path
1         1311 Nov 8 2021 18:58:00 +00:00 startup-config.bak
2         1351 Nov 8 2021 19:08:26 +00:00 startup-config.ftp

66867200 bytes available (8192 bytes used)

R1#more flash:/startup-config.ftp
!
! Last configuration change at 19:07:06 UTC Mon Nov 8 2021 by admin
! NVRAM config last updated at 19:07:13 UTC Mon Nov 8 2021 by admin

...

ntp clock-period 17179848
ntp server 192.168.1.10
!
end
R1#
```

If anything goes wrong with the transfer, enter the following commands:

```debug ip ftp```

You will receive verbose feedback about the transfer, allowing you to debug any problems.

Of course, you can copy a file from the NVRAM to flash memory directly and vice versa:

```
copy nvram:/startup-config flash:/startup-config.alt
copy flash:/startup-config.bak nvram:/startup-config
```

However, do not copy a file into NVRAM that is not supposed to be there! NVRAM has a limited amount of memory (sometimes less than 1 MB), and it is for configuration files, etc.

>**NOTE** - TRUST ME! You do not want to play with the NVRAM, unless you have half a day to spare to transfer the IOS image over xmodem (if everything goes well :rage:). But if you want to take a peek:
> 
>```
>R1#configure terminal
>Enter configuration commands, one per line.  End with CNTL/Z.
>R1(config)#do dir nvram:
>Directory of nvram:/
>
>  147  -rw-        1332                    <no date>  startup-config
>  148  ----        1920                    <no date>  private-config
>    1  -rw-           0                    <no date>  ifIndex-table
>
>155640 bytes total (151312 bytes free)
>R1(config)#exit
>R1#
>```

---
## Securely connect to a network device

Until now, you have been using Telnet to interact with the device. As we stated before, Telnet is not secure. Neither credentials nor data transferred through Telnet is encrypted. A better option is to access the device using the Secure Shell (SSH) protocol.

>**NOTE** - For a great story about SSH from its creator, Tatu Ylonen, check out [How SSH port became 22](https://www.ssh.com/academy/ssh/port "How SSH port became 22")

SSH uses public key cryptography to authenticate users first, then encrypts the data transmitted using an industry-approved cipher. It is the preferred method of communicating with devices remotely.

>**NOTE** - Knowing how public key cryptography and the secure sockets layer (SSL) handshake works is vital if you are planning on working with networks. However, both of these topics are outside the scope of this tutorial, but there are many resources on the Internet, such as [The SSL/TLS Handshake: an Overview](https://www.ssl.com/article/ssl-tls-handshake-overview/ "The SSL/TLS Handshake: an Overview") and others.

However, SSH requires some setup before it can be used. The good news is that you have done much of this work already, such as enabling Layer 3 communications; updating the system clock using an NTP service; and securing the VTY lines with a username and password. Now, generate the Rivest, Shamir, and Adelman (RSA) key pairs the device will need for public key cryptography:

```
configure terminal
crypto key generate rsa general-keys label ADVENTURES modulus 1024
```

After a few seconds, you will see the following output:

```
The name for the keys will be: ADVENTURES

% The key modulus size is 1024 bits
% Generating 1024 bit RSA keys, keys will be non-exportable...[OK]

R1(config)#
```

Before you continue, let's talk about the last command you typed in. As we said, the ```crypto key generate``` command is used to generate the key pairs your device will need to securely connect to the host. In this case, you used the RSA algorithm for the device's digital signature (the other option is the Digital Signature Algorithm (DSA)), and you wanted to generate a set of general-purpose keys, as opposed to key pairs for a specific task. The next option, ```label ADVENTURES``` is a unique identifier for the generated keys; you can maintain multiple sets of keys for different purposes.

Regarding the final option, ```modulus 1024```, and without getting into how the RSA algorithm works, the larger the modulus, the harder it will be to break the keys, but the longer it will take to generate the keys.

>**NOTE** - When automating tasks, you need to keep these delays in mind, otherwise, you will be running commands on top of each other. For example, a Cisco 4700 may take four seconds to generate a key pair using a 1024-bit modulus, while it may take an older Cisco 2500 over four minutes to do the same thing! Sending a command before another command has finished processing will cause your scripts to fail.

The default modulus is 1024 bits, which can be used for the latest version, SSH-2. The recommended size is 2048 bits and the latest maximum size that Cisco allows is 4096 bits. However, SSH version 1 can only use keys up to 768 bits; remember this when generating keys to speak with older devices and hosts that can only use SSH-1. 

Since the modulus of the keys the device generated was greater than 768 bits, you can use SSH-2. Enter the following commands to set the SSH version:

```
ip ssh version 2
end
write memory
show ip ssh
```

After a few seconds, you will see the following output:

```
SSH Enabled - version 2.0
Authentication timeout: 120 secs; Authentication retries: 3
R1#
```

>**NOTE** - If you see ```SSH Enabled - version 1.99```, reset the SSH version to 2 again. SSH 1.99 is not an SSH version; it just means that the device supports SSH-1 and SSH-2. You want to use SSH-2.

To see the keys, enter the following command:

```show crypto key mypubkey rsa```

Exit Telnet by pressing <kbd>Ctrl</kbd>+<kbd>]</kbd>, and inputting <kbd>q</kbd>. Once you have exited Telnet, go to the GNS3 GUI and reload the device:

![Reload the Device](../../img/b01.png)

Go back to the Linux Terminal and attempt to SSH into the device using the username and the IP address:

```ssh admin@192.168.1.20```

After a few seconds, you will see the following output:

```
The authenticity of host '192.168.1.20 (192.168.1.20)' can't be established.
RSA key fingerprint is SHA256:cpoYeqhnSJxDE/Qv1X1LRJH9hrh8fPB8sfD8ELfvTr8.
RSA key fingerprint is MD5:26:ac:35:27:98:0e:82:11:b0:e8:b6:2a:3d:5f:cf:ea.
Are you sure you want to continue connecting (yes/no)?
```

Most computers keep "known" IP addresses in a known_hosts file in the user's hidden .ssh directory. Since this IP address is not in that file, the host wants to know if it can be trusted. It also provides you with hashes of the RSA key fingerprint, so you can verify the device using the ssh-keygen utility.

Enter ```yes``` to continue connecting and enter the VTY password when prompted:

```
Warning: Permanently added '192.168.1.20' (RSA) to the list of known hosts.
Password: 

R1#
```

>**NOTE** - Later, as you continue to connect and reconnect to devices, you may encounter the following message:
>
>```
>@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
>@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
>@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
>IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!
>Someone could be eavesdropping on you right now (man-in-the-middle attack)!
>It is also possible that a host key has just been changed.
>```
>
>If you are certain that only you and the device are connected to each other, the IP address may already exist in the ```known_hosts``` file. Open the file and remove the IP address:
> 
>```vim ~/.ssh/known_hosts```
> 
>If you use the host only to configure devices using the same IP address, you can delete the file completely:
> 
>```rm ~/.ssh/known_hosts```

---
## Securely transfer files to and from a network device

There are several ways to securely copy files to and from a device, such as using the Secure Copy Protocol (SCP) or the SSH File Transfer Protocol (SFTP). You will be using SCP for the lab.

Like SSH, SCP requires some setup before it can be used. The good news is that you have done all the work already! You have enabled Layer 3 communications; updated the system clock using an NTP service; secured the VTY lines with a username and password; and generated the RSA key pairs required for authentication.

Enter the following commands:

```
configure terminal
ip scp source-interface FastEthernet0/0
end
write memory
```

This tells the device to use the FastEthernet port 0/0 for all SCP transfers.

Next, transfer the file from the device to the host:

>**NOTE** - Be careful! By default, SCP places files in the remote host's user's home directory. If you want to use another directory, such as the ```/var/lib/tftpboot/``` directory, use two backslashes after the IP address:
>
> ```copy nvram:/startup-config scp://gns3user@192.168.1.10//var/lib/tftpboot/startup-config.scp```
>
>Otherwise, SCP will fail, attempting to place the file in a non-existent ```var/lib/tftpboot``` directory within your user home directory (e.g. ```/home/gns3user/var/lib/tftpboot/scp_start.cfg```).

```copy nvram:/startup-config scp://gns3user@192.168.1.10/startup-config.scp```

You will be prompted to confirm the remote host's IP address, the remote host's username, and destination filename. You've already provided that information; press <kbd>Enter</kbd> each time:

```
Address or name of remote host [192.168.1.10]? 
Destination username [gns3user]? 
Destination filename [startup-config.scp]? 
```

After a few seconds, you will see the following output. Enter the ***remote host's password*** when prompted:

```
Writing startup-config.scp 
Password: 
! Sink: C0644 1408 startup-config.scp

1408 bytes copied in 8.952 secs (157 bytes/sec)
R1#
```

If you open another Linux Terminal and enter the following command, you will see the backup file and its contents:

```
ll /var/lib/tftpboot
cat /var/lib/tftpboot/startup-config.scp
```

Go back to the SSH terminal. If anything goes wrong with the transfer, enter the following commands:

```debug scp all```

You will receive verbose information about the transfer, allowing you to debug any problems.

Exit by entering ```exit``` at the **Privileged EXEC Mode** prompt. If, for some reason, that does not work, press <kbd>Enter</kbd>, followed by <kbd>~</kbd>.

---
## Shutdown

Before you finish, you will want to shut down all the services you started. Aside from the fact that they use resources, leaving unused services open and available gives threat actors more avenues to hack your system, which is not a good thing. Enter the following commands to shut things down (enter the host's password if prompted):

### Telnet Client

```sudo firewall-cmd --zone=public --remove-port=23/tcp```

### File Transfer Protocol (FTP) Service

```
sudo firewall-cmd --zone=public --remove-port=21/tcp
sudo firewall-cmd --zone=public --remove-service=ftp
sudo systemctl stop vsftpd
sudo sed -i '/ftp_username=nobody/d' /etc/vsftpd/vsftpd.conf
```

### Network Time Protocol (NTP) Service

```
sudo firewall-cmd --zone=public --remove-port=123/udp
sudo firewall-cmd --zone=public --remove-service=ntp
sudo systemctl stop ntpd
sudo sed -i '/server 127.127.1.0/d' /etc/ntp.conf
```

### Trivial File Transfer Protocol (TFTP) Service

```
sudo firewall-cmd --zone=public --remove-port=69/udp
sudo firewall-cmd --zone=public --remove-service=tftp
sudo systemctl stop tftp
```

### Secure Shell (SSH) Protocol Port

```sudo firewall-cmd --zone=public --remove-port=22/tcp```

---
## Congratulations!

Nicely done! Now that you have walked through common tasks and their commands through the Cisco command-line interface (CLI), you can begin to automate them using Python and Pexpect. Go to Lab 1 when you are ready and good luck!
