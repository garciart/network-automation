# Welcome to the Labs!

![All Devices Started](../img/adventures-automation.gif)

These labs will show you how to automate simple network tasks using Python:

- Accessing a network device's Privileged EXEC Mode
- Formatting a network device's flash memory
- Setting a network device's clock
- Getting information about a network device
- Enabling Layer 3 communications to and from a network device
- Securing a network device
- Transferring files to and from a network device
- Securely connecting to a network device
- Securely transferring files to and from a network device

However, before starting the labs, run these commands through the Cisco command-line interface (CLI), as you would do with a real network device. This will give you an idea of what to look for and what to expect from each lab.

>**NOTE** - This tutorial is primarily for Python programmers who are learning about network engineering. If you are a network engineer or know basic Cisco CLI commands, you can skip to the first lab.

First, ensure you have installed GNS3 per the instructions in the [Adventures in Automation](../README.md "Adventures in Automation") tutorial (this repo's main README.md file) and start it up. As we stated in the post script of that tutorial, we recommend you enter ```gns3_run``` from a Terminal to use GNS3.

>**NOTE** - By the way, you will continue to use the Cisco 3745 Multi-Service Access Router for the labs, so no further configuration is needed. All you will have to do from the GNS3 GUI is start the device; occasionally get some info or reload the device; and stop the device before exiting. 

Second, make sure services required for the labs exist on the host. The services include:

1. Network Time Protocol (NTP) - Some network devices may not have a battery-supported system clock, which means that they do not retain the correct time and date after they are powered off, reloaded, or restarted. However, several tasks, such as logging or synchronization, depend on an up-to-date clock. By enabling an NTP service, the device can update its clock using the host's clock.
2. Trivial File Transfer Protocol (TFTP) - TFTP is a very simple file transfer protocol. It uses User Datagram Protocol (UDP) and no encryption, so it is neither reliable nor secure for large file transfers. However, it is good for transferring small files, such as device configuration files, over direct connections, such as through a Console or Auxiliary port. 

Check their statuses by entering the following commands:

```
systemctl status tftp
systemctl status ntp
```

After a few seconds, you will see the following output:

```
[gns3user@localhost ~]$ systemctl status tftp
● tftp.service - Tftp Server
   Loaded: loaded (/usr/lib/systemd/system/tftp.service; indirect; vendor preset: disabled)
   Active: inactive (dead)
     Docs: man:in.tftpd
[gns3user@localhost ~]$ systemctl status ntpd
● ntpd.service - Network Time Service
   Loaded: loaded (/usr/lib/systemd/system/ntpd.service; disabled; vendor preset: disabled)
   Active: inactive (dead)
[gns3user@localhost ~]$ 
```

>**NOTE** - If you see ```Unit tftp.service could not be found.``` or ```Unit ntpd.service could not be found.```, the services are not installed or loaded. Make sure you installed GNS3 per the instructions in the [Adventures in Automation](../README.md "Adventures in Automation") tutorial.

Now that you know the services exist, change your firewall settings by opening a Linux Terminal window and entering the following commands. If prompted, enter your sudo password:

```
sudo firewall-cmd --zone=public --add-port=23/tcp
sudo firewall-cmd --zone=public --add-port=69/udp
sudo firewall-cmd --zone=public --add-service=tftp
sudo firewall-cmd --zone=public --add-port=123/udp
sudo firewall-cmd --zone=public --add-service=ntp
```

The first command allows Telnet client communications through port 23, while the next two commands allow TFTP client and server communications through port 69. The final two commands permit NTP traffic, allowing the host to act as an NTP server.

>**NOTE** - Both Telnet and TFTP are not secure, but you will use them in the labs to demonstrate simple host-to-device communications and file transfers, before implementing more secure protocols. 

>**NOTE** - If you run into any errors, make sure you installed GNS3 per the instructions in the [Adventures in Automation](../README.md "Adventures in Automation") tutorial.
> - Do not reload the firewall daemon. For security purposes, these changes are temporary and the ports will close if the system crashes or reboots.
> - Do not install a Telnet service. You will only need the Telnet client, which you installed during the GNS3 setup. 

Next, create the TFTP default directory (if it does not exist) and give it the necessary permissions to accept and send files:

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

```
sudo systemctl start tftp
```

For the NTP service, you may need to make some modifications to the host system. First, check if the host is configured as an NTP server by looking for the reserved NTP server address:

```
grep "server 127.127.1.0" /etc/ntp.conf
```

You should see the search string, ```server 127.127.1.0```, repeated back in red. If not, append the local server information to the NTP configuration file, using the following command:

```
echo -e "server 127.127.1.0" | sudo tee -a /etc/ntp.conf
```

Finally, start the NTP service:

```
sudo systemctl start ntp
```

Now that you have set up the host system, you can run the commands in a Console port session. First, get the gateway IP address and Console port's number from the **Topology Summary** in the top left-hand corner.:

![Topology Summary](../img/a32.png)

If the Console port number is difficult to see, you can get the information by expanding the dock or right-clicking on the R1 node and selecting **Show node information**:

![Show Node Information](../img/a35.png)

![Node Information](../img/a36.png)

Connect to the device using Telnet. In your case, the Console port number is ```5001```:

```
telnet 192.168.1.1 5001
```

Not to be overly dramatic, but after you input that command, ***STOP!*** You may scroll, but do not press <kbd>Enter</kbd> or input any more commands yet.

You will see messages from the boot sequence of the device appear on the screen:

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

```
Press RETURN to get started!
```

If the device was reloaded correctly, this line will appear near the end of the boot sequence. However, you should see no prompts (e.g., ```R1>```, ```R1#```, etc.). If you see any prompts, especially a prompt followed by a command (e.g., "```R1#configure terminal```", etc.), that means that the device was not properly reloaded, and you may be using someone else's virtual teletype (VTY) session. This is dangerous for many reasons, since you may be eavesdropping on another user's session or creating a race condition by simultaneously entering commands at the same time as another user.

>Unfortunately, entering the ```reload``` command in GNS3 will cause the Console terminal to "hang", so if you do see a prompt, exit Telnet by pressing <kbd>Ctrl</kbd>+<kbd>]</kbd>, and inputting <kbd>q</kbd>. Once you have exited Telnet, go to the GNS3 GUI and reload the device:
>
>![Reload the Device](../img/b01.png)

If you do not see a prompt, press <kbd>Enter</kbd> now. If the following text appears...

```
User Access Verification

Password: 
```

...it means that the device has already been configured by someone else. There is nothing wrong with that, and, as long as you have permission and the proper credentials, you can automate tasks for the device. However, for your labs, you need to use an unconfigured device.

>Unfortunately, there is no easy way to reset the device to its factory settings in GNS3; you will have to delete the device in the GNS3 workspace, and replace it with a new device.

>***If this is the first time you are using GNS3, other than in the [Adventures in Automation](../README.md "Adventures in Automation") tutorial, you should not run into an improperly reloaded device, an open virtual teletype session, or a previously configured device. We only cover these potentially dangerous situations to allow you to recognize them in real life, when configuring an actual device for Layer 3 communications.***

Otherwise, if you press <kbd>Enter</kbd>, and you are greeted with a simple ```R1#```, you are good to go. You are in **Privileged EXEC Mode**, the default startup mode for most Cisco devices:

```
R1#
```

Some devices may display an ```R1>``` prompt instead. This means you are in **User EXEC Mode**, an interface that allows limited configuration and interaction with the device. Enter the following command to reach **Privileged EXEC Mode**:

```
enable
```

If you are prompted for a password, this means that the device has already been configured. Unfortunately, as we stated earlier, to run the labs, you will have to delete the device in the GNS3 workspace, and replace it with a new device.

However, if all is well, the first thing you want to do is to format the device's built-in CompactFlash (CF) memory card. If you scroll through the startup output, you may see the following status message:

```
*Mar  1 00:00:04.135: %PCMCIAFS-5-DIBERR: PCMCIA disk 0 is formatted from a different router or PC. A format in this router is required before an image can be booted from this device
```

The Cisco 3745's PCMCIA disk 0, known as ```flash:```, is used to store the system image, configuration files, and more. While you can take a chance and hope the memory card works this device, it is better to format it before configuring the device. Therefore, enter the following command:

```
format flash:
```

You will be prompted twice to confirm. Press <kbd>Enter</kbd> each time:

```
Format operation may take a while. Continue? [confirm]
Format operation will destroy all data in "flash:".  Continue? [confirm]
```

If the device's memory and disks were configured correctly in [Adventures in Automation](../README.md "Adventures in Automation"), you should see the following output:

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

Next, you will set the device's clock. As we stated earlier, this is a simple, but very important, task, since tasks, such as logging or synchronization, depend on an up-to-date clock. To this manually, enter the following command:

```
clock set 12:00:00 Jan 1 2021
```

After a few seconds, you will see the following output:

```
*Jan  1 12:00:00.000: %SYS-6-CLOCKUPDATE: System clock has been updated from 00:24:57 UTC Fri Mar 1 2002 to 12:00:00 UTC Fri Jan 1 2021, configured from console by console.
R1#
```

Unfortunately, our device will not retain manual clock settings after reload. Luckily, you activated an NTP service on the host; the device can use it to update its clock. Do this by entering the following command:

```
configure terminal
ntp server 192.168.1.10
end
show ntp status
show clock

```

After a few seconds, you will see the following output:

```
R1#show ntp status
Clock is unsynchronized, stratum 16, no reference clock
nominal freq is 250.0000 Hz, actual freq is 250.0000 Hz, precision is 2**18
reference time is E532E1B1.AA29D0D3 (23:37:21.664 UTC Sun Nov 7 2021)
clock offset is 4891.1245 msec, root delay is 98.69 msec
root dispersion is 20805.36 msec, peer dispersion is 16000.00 msec
R1#show clock
23:37:39.071 UTC Sun Nov 7 2021
```

Your devices clock should match your system clock, offset for Coordinated Universal Time (UTC).

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
>```
>ip address show | grep '[0-9]: e[mnt]'
>```
>
>Note the name of the isolated interface from the [Adventures in Automation](../README.md "Adventures in Automation") tutorial (e.g., ```enp0s8```, etc.):
>
>```
>2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
>3: enp0s8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast master br0 state UP group default qlen 1000
>```
>
>Reapply an IP address to the interface:
>
>```
>sudo ip address replace 192.168.1.10/24 dev enp0s8
>```
>
>Attempt to ping the host from the device once again. If the success rate is still zero, go back and review the steps in the [Adventures in Automation](../README.md "Adventures in Automation") tutorial.

Before continuing, make that change to the interface permanent by updating the device's **startup configuration**; otherwise, the device will shutdown the interface after each reload or reboot:

```
write memory
```

After a few seconds, you will see the following output:

```
Building configuration...
[OK]
R1#
```

>**NOTE** - Most Cisco devices have two configuration files:
> 1. **running-configuration** - This file keeps track of all changes to the device's configuration for the current session. It is held in the device's volatile RAM, and the file, along with any changes, are discarded when the device is turned off or reloaded, unless saved to the startup-configuration file. 
> 2. **startup-configuration** - This file is stored in the device's nonvolatile random-access memory (NVRAM) and is read by the device upon startup. Any changes to the device's configuration must be saved to this file to become permanent. 

Exit Telnet by pressing <kbd>Ctrl</kbd>+<kbd>]</kbd>, and inputting <kbd>q</kbd>. Once you have exited Telnet, go to the GNS3 GUI and reload the device:

![Reload the Device](../img/b01.png)

Now, at the Linux prompt, attempt to Telnet into the device using the IP address:

```
telnet 192.168.1.20
```

After a few seconds, you will see the following output:

```
Trying 192.168.1.20...
Connected to 192.168.1.20.
Escape character is '^]'.

Password required, but none set
Connection closed by foreign host.
```

![What???](../img/whaat-huh.gif "What???")

When you made your changes permanent, the current running configuration added this line to the end of the device's startup configuration, stored in the device's nonvolatile random-access memory (NVRAM):

```
line vty 0 4
 login
```

The Cisco 3745 has five virtual teletype (VTY) lines (0 through 5). As a fail-safe, the device requires a login whenever a user attempts to access it through a VTY line, as you just attempted to do. The problem is that you never set a password for the VTY line, so the device cannot let you in. 

You have several options. 

1. One way is to continue directly connecting to the Console port, but, as we stated earlier, our goal is to automate tasks, such as IOS updates and reconfigurations, and perform them remotely. In addition, imagine you had to update each router in each cabinet for a data center with 100+ cabinets; it would take a long time. 
2. Another way is to change the configuration, by replacing ```login``` with ```no login```, removing the authentication requirement.
3. However, the best option is to secure the lines; whenever you can, "err" on the side of security.

So, in the Linux Terminal, telnet back into the device through the Console port:

```
telnet 192.168.1.1 5001
```

Now you will secure the VTY line. Set the username to ```admin```, the privilege level to "15", and the password to ```cisco```:

>**NOTE** - Cisco devices have 16 privilege levels (0 through 15). 13 are customizable, while three are set by the IOS:
> - 0 - No privileges
> - 1 - Read-only and access to the ping command
> - 15 - Full access, including reading and writing configuration files
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
> - In real life, make sure you use better passwords.
> - The maximum length for a Cisco password is **64** characters and some special characters are allowed.
> - Never add comments after a Cisco password; they will be included in the password.
> - Check out [xkcd's take on passwords](https://xkcd.com/936/ "xkcd:Password Strength").

To test your security, exit **Privileged EXEC Mode**:

```
disable
```

You are greeted with the **User EXEC Mode** prompt:

```
R1>
```

Attempt to re-enter **Privileged EXEC Mode**:

```
enable
```

When prompted for a password, enter the **Privileged EXEC Mode** (i.e., ```cisen```). You should see the **Privileged EXEC Mode** prompt:

```
R1#
```

>**NOTE** - If something went wrong, attempt to reconfigure the passwords again. However, if you are stuck in **User EXEC Mode**, you will have to delete the device in the GNS3 workspace, and replace it with a new device.

Before you go on, take a look at the startup configuration file:

```
show startup-config
```

You should see something similar to the following output:

```
Using 1118 out of 155640 bytes
!
! Last configuration change at 12:00:46 UTC Fri Jan 1 2021
! NVRAM config last updated at 12:00:50 UTC Fri Jan 1 2021
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
ntp server 192.168.1.10
!
end
```

>**NOTE** - Don't worry about the exclamation points; they usually precede comments, and the Cisco command parser automatically includes them to make configuration files more readable.

There's a lot of good information in this file, but what is worrisome is the fact that we are not employing encryption and the passwords are all in plain text!

```
no service password-encryption
...
enable password cisen
...
username admin password 0 cisco
...
line con 0
 password ciscon
...
line aux 0
 password cisaux
```

Fix the **Privileged EXEC Mode** password first by removing the plain text and replacing it with a hashed password. FYI, Cisco uses its own MD5 hash algorithm with a salt, resulting in a 30-character string:

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

Finally, obscure the Console port and Auxiliary port passwords by enabling the password encryption service. FYI, these passwords are encrypted using a reversible Vigenère cipher, not a hashing algorithm, resulting in a 14-character alphanumeric string:

```
configure terminal
service password-encryption
end
write memory
```

Take another look at the startup configuration file:

```
show statup-config
```

You should see changes similar to the following:

```
service password-encryption
...
enable secret 5 $1$GTon$HkSl2mJ3D8OB3lvCgNzK.0
...
username admin privilege 15 secret 5 $1$B2kV$6zQIQSPqM05TZzHh4NCPx1
...
line con 0
 password 7 05080F1C224340
...
line aux 0
 password 7 121A0C04131E14
```

Exit Telnet by pressing <kbd>Ctrl</kbd>+<kbd>]</kbd>, and inputting <kbd>q</kbd>. Once you have exited Telnet, go to the GNS3 GUI and reload the device:

![Reload the Device](../img/b01.png)

Now, at the Linux prompt, attempt to Telnet into the device using the IP address:

```
telnet 192.168.1.20
```

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

If you made it this far, congratulations! Our next step is to back up and save the startup configuration.

