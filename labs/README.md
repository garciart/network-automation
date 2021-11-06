# Welcome to the Labs!

![All Devices Started](../img/adventures-automation.gif)

Before starting the labs, let's run the commands we will use in the labs in a console session, as we would do with a real router. This will give you an idea of the output and results expected from each lab.

First, ensure you have installed GNS3 per the instructions in the **"Adventures in Automation"** tutorial (this repo's main README.md file) and start it up. As we stated at the end, we recommend you enter ```gns3_run``` from a Terminal to start GNS3.

>**NOTE** - By the way, we will continue to use the Cisco 3745 Multi-Service Access Router for the labs, so no further configuration is needed. All you will have to do from the GNS3 GUI is start the device; occasionally get some info or reload the device; and stop the device before exiting. 

Second, change your firewall settings by opening a Linux Terminal window and entering the following commands. If prompted, enter your sudo password:

```
sudo firewall-cmd --zone=public --add-port=23/tcp
sudo firewall-cmd --zone=public --add-port=69/udp
sudo firewall-cmd --zone=public --add-service=tftp
```

The first command allows Telnet client communications through port 23, while the next two commands allow Trivial File Transfer Protocol (TFTP) client and server communications through port 69. Both Telnet and TFTP are not secure, but we will use them in the labs to demonstrate simple host-to-device communications and file transfers, before implementing more secure protocols.

>**NOTE** - If you run into any errors, make sure you installed GNS3 per the instructions in the "Adventures in Automation" tutorial.
>- Do not reload the firewall daemon. For security purposes, these changes are temporary and the ports will close if the system crashes or reboots.
>- Do not install a Telnet service. You will only need the Telnet client, which you installed during the GNS3 setup. 

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

Now that you have set up the host system, you can run the commands in a router console session. First, get the gateway IP address and console port's number from the **Topology Summary** in the top left-hand corner.:

![Topology Summary](../img/a32.png)

If the console port number is difficult to see, you can get the information by expanding the dock or right-clicking on the R1 node and selecting **Show node information**:

![Show Node Information](../img/a35.png)

![Node Information](../img/a36.png)

Connect to the device using Telnet. In our case, the console port number is ```5001```:

```
telnet 192.168.1.1 5001
```

Not to be overly dramatic, but after you input that command, ***STOP!*** You may scroll, but do not press <kbd>Enter</kbd> or input any more commands yet.

If everything was configured correctly, you will see messages from the boot sequence of the device. For us, the most important message is:

```
Press RETURN to get started!
```

If the device was reloaded correctly, you should see this line at the end of the boot sequence of the device (don't worry if some status messages appear afterwards):

```
SETUP: new interface FastEthernet0/0 placed in "shutdown" state
SETUP: new interface FastEthernet0/1 placed in "shutdown" state

Press RETURN to get started!

sslinit fn

*Mar  1 00:00:03.871: %LINEPROTO-5-UPDOWN: Line protocol on Interface VoIP-Null0, changed state to up
*Mar  1 00:00:03.927: %SYS-5-CONFIG_I: Configured from memory by console
*Mar  1 00:00:04.087: %SYS-5-RESTART: System restarted --
```

However, you should see no prompts (e.g., ```R1>```, ```R1#```, etc.). If you see any prompts, especially a prompt followed by a command (e.g., "```R1#configure terminal```", etc.), that means that the device was not properly reloaded, and you may be using someone else's virtual teletype (VTY) session. This is dangerous for many reasons, since you may be eavesdropping on another user's session or creating a race condition by simultaneously entering commands at the same time as another user. Unfortunately, entering the ```reload``` command in GNS3 will cause the console terminal to "hang", so if you do see a prompt, exit Telnet by pressing <kbd>Ctrl</kbd>+<kbd>]</kbd>, and inputting <kbd>q</kbd>. Once you have exited Telnet, go to the GNS3 GUI and reload the device:

![Reload the Device](../img/b01.png)

Otherwise, if you do not see a prompt, press <kbd>Enter</kbd> now. If you see the following text...

```
User Access Verification

Password: 
```

...it means that the device has already been configured by someone else. Unfortunately, there is no easy way to reset the device in GNS3; you will have to delete the device in the GNS3 workspace, and replace it with a new device.

***If this is the first time you are using GNS3, other than in the "Adventures in Automation" tutorial, you should not run into an improperly reloaded device, an open virtual teletype session, or a pre-configured device. We only cover these potentially dangerous situations to allow you to recognize them in real life, when configuring an actual device for Layer 3 communications.***

Otherwise, if you press <kbd>Enter</kbd>, and you are greeted with a simple ```R1#```, you are good to go. You are in **Privileged EXEC Mode**, the default startup mode for most Cisco devices:

```
R1#
```

Some devices may display an ```R1>``` prompt instead. This means you are in **User EXEC Mode**, an interface that allows limited configuration and interaction with the device. Enter the following command to reach **Privileged EXEC Mode**:

```
enable
```

If you are prompted for a password, this means that the device has already been configured. Unfortunately, as we stated earlier, you will have to delete the device in the GNS3 workspace, and replace it with a new device.

However, if all is well, the first thing we want to do is to format the device's built-in CompactFlash (CF) memory card. If you scroll through the startup output, you may see the following status message:

```
*Mar  1 00:00:04.135: %PCMCIAFS-5-DIBERR: PCMCIA disk 0 is formatted from a different router or PC. A format in this router is required before an image can be booted from this device
```

The Cisco 3745's PCMCIA disk 0, known as ```flash:```, is used to store the system image, configuration files, and more. While you can take a chance and hope the memory card works this device, it is better to format it before configuring the device:

```
R1#format flash:
```

You will be prompted twice to confirm. Press <kbd>Enter</kbd> each time:

```
Format operation may take a while. Continue? [confirm]
Format operation will destroy all data in "flash:".  Continue? [confirm]
```

If the device's memories and disks tab was configured correctly in "Adventures in Automation", you should see the following output:

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

Next, 