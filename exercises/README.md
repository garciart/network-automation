# Exercises

The exercises on this page will show you how to automate basic network tasks using Python. Each exercise will walk through the manual way of performing a task, followed by a Python script that automates the work.

First, ensure you have installed and started GNS3, per the instructions on the landing page of this **[repo](https://github.com/garciart/network-automation#adventures-in-network-automation "Adventures in Network Automation")**, up to and including **[Your First Exercise - Part 1: Create the Network](https://github.com/garciart/network-automation#part-1-create-the-network "Your First Exercise - Part 1: Create the Network")**.

>**NOTE** - To speed things up, we recommend you follow our suggestion in the post-script of **[Adventures in Automation](https://github.com/garciart/network-automation#post-script "Post Script")**, and start GNS3 by using the ```gns3_run``` Bash script.

However, add another **Cisco 3745** router to the Workspace, and make sure it is named "R2". Connect the ```tap1``` interface in **Cloud1** to the ```F0/0``` interface in **R2**. Start all the devices, and you should end up with a topology that looks like the following:

![All Devices Started](../img/b00.png)

>**NOTE** - If your port numbers in the **Topology Summary** (in the top right of the GNS3 GUI) are not ```5001``` and ```5002```, that is OK. For the exercises, replace ```5001``` with the port number that the GNS3 server assigned to **R1** (e.g., ```192.168.1.1 5011```, etc.) and replace ```5002``` with the port number that the GNS3 server assigned to **R2**.

You will run commands directly in the console on **R1**, and you will run Python scripts on **R2**. This will prevent errors due to repeating commands on the same device.

## Exercises

>**NOTE** - In the code snippets, a semicolon (```;```) or pound sign (```#```), after a command or between lines of code, is a comment indicator, in which I may explain what is going on. They are optional, and you do not have to add the indicator or the comments.

>**NOTE** - While I included error-handling in the [Cisco IOS class](cisco_ios.py "Cisco IOS class") and the [static Utility module](utility.py "static Utility module"), for the sake of brevity, I did not do so for these exercises. I expect that, if you followed the instructions and created your topology correctly, all the commands will work, if executed sequentially.

1. [Connect to the device from the host via Telnet](#connect-to-the-device-from-the-host-via-telnet "Connect to the device from the host via Telnet")
2. [Access the Privileged EXEC mode of the device](#access-the-privileged-exec-mode-of-the-device "Access the Privileged EXEC mode of the device")
3. [Set up the logging process for the device](#set-up-the-logging-process-for-the-device "Set up the logging process for the device")
4. [Change the hostname of the device](#change-the-hostname-of-the-device "Change the hostname of the device")
5. [Update the startup configuration of the device](#update-the-startup-configuration-of-the-device "Update the startup configuration of the device")
6. [Identify the default file system of the device](#identify-the-default-file-system-of-the-device "Identify the default file system of the device")
7. [Get the name of the device](#get-the-name-of-the-device "Get the name of the device")
8. [Get the serial number of the device](#get-the-serial-number-of-the-device "Get the serial number of the device")
9. [Get the operating system version of the device](#get-the-operating-system-version-of-the-device "Get the operating system version of the device")
10. [Format a file system on the device](#format-a-file-system-on-the-device "Format a file system on the device")
11. [Assign the router an IPv4 address](#assign-the-router-an-ipv4-address "Assign the router an IPv4 address")
12. [Test connectivity from the device to the host](#test-connectivity-from-the-device-to-the-host "Test connectivity from the device to the host")
13. [Test connectivity from the host to the device](#test-connectivity-from-the-host-to-the-device "Test connectivity from the host to the device")
14. [Secure the virtual teletype (VTY) lines](#secure-the-virtual-teletype-vty-lines "Secure the virtual teletype (VTY) lines")
15. [Secure the console and auxiliary ports](#secure-the-console-and-auxiliary-ports "Secure the console and auxiliary ports")
16. [Secure the Privileged EXEC Mode](#secure-the-privileged-exec-mode "Secure the Privileged EXEC Mode")
17. [Set the device clock manually](#set-the-device-clock-manually "Set the device clock manually")
18. [Enable the NTP server on the host](#enable-the-ntp-server-on-the-host "Enable the NTP server on the host")
19. [Update the device clock using the host NTP server](#update-the-device-clock-using-the-host-ntp-server "Update the device clock using the host NTP server")
20. [Enable secure communications with the device](#enable-secure-communications-with-the-device "Enable secure communications with the device")
21. [Connect to the device from the host via Secure Shell (SSH)](#connect-to-the-device-from-the-host-via-secure-shell-ssh "Connect to the device from the host via Secure Shell (SSH)")
22. [Enable the TFTP server on the host](#enable-the-tftp-server-on-the-host "Enable the TFTP server on the host")
23. [Download the device startup configuration to the host via TFTP](#download-the-device-startup-configuration-to-the-host-via-tftp "Download the device startup configuration to the host via TFTP")
24. [Determine and display the hash value of a file](#determine-and-display-the-hash-value-of-a-file "Determine and display the hash value of a file")
25. [Upload a non-existing file from the host to the device via TFTP](#upload-a-non-existing-file-from-the-host-to-the-device-via-tftp "Upload a non-existing file from the host to the device via TFTP")
26. [Download a non-existing file from the host to the device via TFTP](#download-a-non-existing-file-from-the-host-to-the-device-via-tftp "Download a non-existing file from the host to the device via TFTP")
27. [Upload an existing file from the host to the device via TFTP](#upload-an-existing-file-from-the-host-to-the-device-via-tftp "Upload an existing file from the host to the device via TFTP")
28. [Download an existing file from the host to the device via TFTP](#download-an-existing-file-from-the-host-to-the-device-via-tftp "Download an existing file from the host to the device via TFTP")
29. [Enable the FTP server on the host](#enable-the-ftp-server-on-the-host "Enable the FTP server on the host")
30. [Prepare the device for FTP transfers](#prepare-the-device-for-ftp-transfers "Prepare the device for FTP transfers")
31. [Download the device startup configuration to the host via FTP](#download-the-device-startup-configuration-to-the-host-via-ftp "Download the device startup configuration to the host via FTP")
32. [Upload a non-existing file from the host to the device via FTP](#upload-a-non-existing-file-from-the-host-to-the-device-via-ftp "Upload a non-existing file from the host to the device via FTP")
33. [Download a non-existing file from the host to the device via FTP](#download-a-non-existing-file-from-the-host-to-the-device-via-ftp "Download a non-existing file from the host to the device via FTP")
34. [Upload an existing file from the host to the device via FTP](#upload-an-existing-file-from-the-host-to-the-device-via-ftp "Upload an existing file from the host to the device via FTP")
35. [Download an existing file from the host to the device via FTP](#download-an-existing-file-from-the-host-to-the-device-via-ftp "Download an existing file from the host to the device via FTP")
36. [Enable the SCP server on the host](#enable-the-scp-server-on-the-host "Enable the SCP server on the host")
37. [Download the device startup configuration to the host via SCP](#download-the-device-startup-configuration-to-the-host-via-scp "Download the device startup configuration to the host via SCP")
38. [Upload a non-existing file from the host to the device via SCP](#upload-a-non-existing-file-from-the-host-to-the-device-via-scp "Upload a non-existing file from the host to the device via SCP")
39. [Download a non-existing file from the host to the device via SCP](#download-a-non-existing-file-from-the-host-to-the-device-via-scp "Download a non-existing file from the host to the device via SCP")
40. [Upload an existing file from the host to the device via SCP](#upload-an-existing-file-from-the-host-to-the-device-via-scp "Upload an existing file from the host to the device via SCP")
41. [Download an existing file from the host to the device via SCP](#download-an-existing-file-from-the-host-to-the-device-via-scp "Download an existing file from the host to the device via SCP")
42. [Reload the device](#reload-the-device "Reload the device")
43. [Disable the TFTP service on the host](#disable-the-tftp-service-on-the-host "Disable the TFTP service on the host")
44. [Disable the FTP service on the host](#disable-the-ftp-service-on-the-host "Disable the FTP service on the host")
45. [Disable the NTP service on the host](#disable-the-ntp-service-on-the-host "Disable the NTP service on the host")
46. [Disable the SCP service on the host (optional)](#disable-the-scp-service-on-the-host-optional "Disable the SCP service on the host (optional)")

---

## Connect to the device from the host via Telnet

As I stated in **[Adventures in Automation](https://github.com/garciart/network-automation "Adventures in Automation")**, GNS3 uses [*Reverse Telnet*](https://en.wikipedia.org/wiki/Reverse_telnet "Reverse Telnet"). The GNS3 server assigns a port number to each virtual device and lists them in the **Topology Summary** (in the top right of the GNS3 GUI). You can access any device through the server's IPv4 address and its console port number. Connecting to a device using Reverse Telnet is similar to connecting to a device through its console port (or auxiliary port, if enabled), using a serial cable, and a terminal emulator like PuTTY or Minicom. However, you will not be able to open a Secure Shell (SSH) connection using this method.

Open a Terminal and connect to the device; this will be your **Console Terminal**:

```
telnet 192.168.1.1 5001
```

>**NOTE** - If you see an error message that states, ```Connection refused```, make sure you started all the devices in the GNS3 client.

After a few minutes, the device will ask you to ```Press RETURN to get started```; it may appear in the middle of the startup messages:

```
SETUP: new interface FastEthernet0/0 placed in "shutdown" state
SETUP: new interface FastEthernet0/1 placed in "shutdown" state

Press RETURN to get started!

sslinit fn

*Mar  1 00:00:03.871: %LINEPROTO-5-UPDOWN: Line protocol on Interface VoIP-Null0, changed state to up
*Mar  1 00:00:03.927: %SYS-5-CONFIG_I: Configured from memory by console
*Mar  1 00:00:04.087: %SYS-5-RESTART: System restarted --
```

>**NOTE** - If you are greeted with a request for a username or password, that means that the device was already configured by someone else. There is nothing wrong with that, as long as you have permission and the proper credentials. However, for these exercises, you will need to use an unsecured and unconfigured device.
>
>Unfortunately, there is no easy way to reset a Dynamips image to its factory settings in GNS3; you will have to delete **R1** in the GNS3 GUI, and replace it with a new device.

Press <kbd>Enter</kbd>, and one of the following prompts should appear:

- ```R1>``` - You are in User EXEC Mode. In this mode, you can only perform basic tasks, like pinging or "show"-ing basic information.
  - ```R1#``` - You are in Privileged EXEC Mode. In this mode, you can perform advanced tasks, like debugging, and you can access the device's global configuration settings.
  - ```R1(config)#``` - You are in Global Configuration Mode. In this mode, you can view and change settings that affect all interfaces, ports, and protocols of the device, and you can access their configuration settings.
  - ```R1(config-if)``` - You are in Interface Configuration Mode. In this mode, you can manage network interface settings, such as setting an IPv4 address.
  - ```R1(config-line)#``` - You are in Line Command Mode. In this mode, you can manage port settings, such as setting a password.
  - ```R1(config-router)#``` - You are in Router Command Mode. In this mode, you can manage routing protocols, such as Routing Information Protocol (RIP), Open Shortest Path First (OSPF), etc.

>**NOTE** - If you did not press <kbd>Enter</kbd>, but a prompt (e.g., ```R1#```, etc.) appeared anyway, that means that the device was not properly reloaded, and you may be using an open session. This is dangerous for many reasons, since you may be eavesdropping on another user's session or creating a race condition by simultaneously entering commands at the same time as another user.
>
>Unfortunately, entering the ```reload``` command when using older Dynamips images, as in this case, will cause the device to "hang".
>
>Press <kbd>Ctrl</kbd> + <kbd>]</kbd>, then enter "q" at the ```telnet>``` prompt, to exit Telnet. Once you have exited Telnet, go back to the GNS3 GUI. Right-click on the device, and select **Stop**, then **Reload**.

***If this is the first time you are using GNS3, other than in the [Adventures in Automation](../README.md "Adventures in Automation") tutorial, you should not run into an improperly reloaded device, an open session, or a previously configured device. We only cover these potentially dangerous situations to allow you to recognize them in real life.***

In these exercises, the base mode for interacting with the device is **Privileged EXEC Mode** (```R1#```). If you are not in Privileged EXEC Mode, that is OK; I'll show you how to get to Privileged EXEC Mode from any mode after this exercise.

>**NOTE** - A real, brand-new device would not boot into any mode, but would ask you one or both of the following questions:
>
>```Would you like to terminate autoinstall? [yes]:```
>
>or
>
>```Would you like to enter the initial configuration dialog? [yes/no]:```
>
>If you answer ```yes``` to the first question, then ```no``` to the second, a mode prompt would then appear. 

Right now, open another Terminal (or another tab in the current Terminal), and access the Python interpreter; this will be your **Python Terminal**:

```
python
```

At the ```>>>``` prompt, enter the following code to create a Telnet child process:

>**NOTE** - Do not run these scripts on **R1**! Make sure you use the port number for **R2** instead, or you will run into problems later on. 

```
import pexpect
child = pexpect.spawn('telnet 192.168.1.1 5002')
```

![Huh?](../img/huh.gif "Huh?")

Wow, nothing happened; how anti-climactic. Do not worry, you will start interacting with the child process in the next exercise.

-----

## Access the Privileged EXEC mode of the device

As I said, the base mode for interacting with the device is **Privileged EXEC Mode**. Go back to your **Console Terminal** and determine which mode you are in:

- If the prompt is ```R1>```, enter ```enable``` to get to Privileged EXEC Mode.
- If the prompt is not ```R1>``` or ```R1#```, enter ```end``` to get to Privileged EXEC Mode.
- If the prompt is ```R1#```, you are good to go!

Go back to your **Python Terminal** and enter the following commands:

>**NOTE** - Press <kbd>Enter</kbd> if you come across a blank line in the code. This will get you out of secondary paths of execution (indicated by a ```...``` prompt in the interpreter), such as loop or if-else mode.

```
device_prompts = ['R2>', 'R2#', 'R2(config)#', 'R2(config-if)#', 'R2(config-line)#', 'R2(config-switch)#', 'R2(config-router)#', ]
child.sendline('\r')
index = child.expect_exact(device_prompts)
# Privileged EXEC Mode is R2# at index 1, aka device_prompts[1]
if index <= 1:
    child.sendline('enable\r')  # OK for R2> and R2# (no effect if already in Privileged EXEC Mode)
else:
    child.sendline('end\r')  # After this line, press Enter again to exit if-else mode

child.expect_exact(device_prompts[1])
```

A ```0``` should appear after you enter the last line, which indicates that the child process found the Privileged EXEC Mode prompt.

>**NOTE - End-of-line (EOL) issues:** Pexpect's ```sendline()``` sends a line feed (```\n```) after the text. However, depending on:
>- The physical port used to connect to the device (e.g., VTY, Console, etc.)
>- The protocol (e.g., Telnet, SSH, etc.)
>- The network port (e.g., 23, 2000, 4000, etc.)
>- The terminal emulator (e.g., PuTTY, Minicom, etc.)
>- The emulation (e.g., VT100, VT102, ANSI, etc.)
>
>The device may require a carriage return (```\r```) before the line feed to create a CRLF combination (i.e., ```child.sendline('text\r')```), based on the connection. For example, when using Telnet with GNS3 and the Cisco 3745 router, you must append a carriage return to the text in each ```sendline()```.

-----

## Set up the logging process for the device

Go back to your **Console Terminal**, then enter and exit **Global Configuration Mode**:

```
configure terminal ; Enter Global Configuration Mode
end ; exit Global Configuration Mode
```

**Output:**: 

```
R1#configure terminal
R1(config)#end
R1#
*Mar  1 00:00:19.347: %SYS-5-CONFIG_I: Configured from console by console
R1#
```

Notice the message that appeared? By default, Cisco devices display system messages on the console, using the following format:

- Sequence Number (if enabled) -```*```
- Timestamp - ```Mar  1 00:00:19.347```
- Source or Facility - ```SYS```
- Severity Level - ```5```
- Message Mnemonic - ```CONFIG_I```
- Description - ```Configured from console by console```

However, ```logging synchronous``` is enabled by default, which means that these messages will not suddenly appear in the middle of a command. Instead, console messages will end with a new prompt, as shown above. When configuring a device using Python, this may cause the Pexpect cursor to stop at the wrong prompt, and look for a search string in the wrong place.

There are several ways to solve this problem:

1. You can disable console logging by entering ```no logging console```. However, doing this will hide important messages, such as messages about software or hardware malfunctions.
2. You can change the console logging level from a [severity](https://en.wikipedia.org/wiki/Syslog#Severity_level "Syslog Severity Levels") of ***7 (Debug)*** to ***2 (Critical)***. Doing this will not hide critical error messages, but Level ***7 (Debug)*** through Level ***3 (Error)*** messages will "disappear", since the device does not store them.
3. You can store messages in a buffer instead.

We will go with choices 2 and 3 for now. Once the device is configured, you can save the messages to a file or forward them to a [syslog server](https://en.wikipedia.org/wiki/Syslog "Syslog").

Go back to your **Console Terminal** and set up the logging process:

```
configure terminal
logging console 2 ; Sets the logging level to 2 (critical)
logging buffered 16384 ; Sets the log buffer to 16 KiB
end
```

Now, once you enter ```end```, no message should appear. But if you look at the log, you will see that the message was stored:

```
show logging
```

**Output:**

```
Syslog logging: enabled (12 messages dropped, 1 messages rate-limited,
                0 flushes, 0 overruns, xml disabled, filtering disabled)
    Console logging: level critical, 12 messages logged, xml disabled,
                     filtering disabled
    Monitor logging: level debugging, 0 messages logged, xml disabled,
                     filtering disabled
    Buffer logging: level debugging, 1 messages logged, xml disabled,
                    filtering disabled
    Logging Exception size (4096 bytes)
    Count and timestamp logging messages: disabled

No active filter modules.

    Trap logging: level informational, 16 message lines logged
          
Log Buffer (16384 bytes):

*Mar  1 00:00:48.355: %SYS-5-CONFIG_I: Configured from console by console
```

Go back to your **Python Terminal** and enter the following commands:

```
child.sendline('configure terminal\r')
child.expect_exact('R2(config)#')
child.sendline('logging console 2\r')
child.expect_exact('R2(config)#')
child.sendline('logging buffered 16384\r')
child.expect_exact('R2(config)#')
child.sendline('end\r')
child.expect_exact('R2#')
```

Check your output for errors. A ```0``` should appear after you enter the last line, which indicates that the child process is back at the Privileged EXEC Mode prompt.

-----

## Change the hostname of the device

Sometimes, the hostname of the device is too generic (e.g., ```Switch```, ```Router```, etc.). If your network has multiple switches or routers, you can lose track of which device you are working on, and you may accidentally enter a command on the wrong device. Making each device's hostname unique can prevent this.

Go back to your **Console Terminal** and change the hostname to ```Router1```:

```
configure terminal ; Enter Global Configuration Mode
hostname Router1
end ; Exit Global Configuration Mode
```

**Output:**

```
R1#configure terminal 
Enter configuration commands, one per line.  End with CNTL/Z.
R1(config)#hostname Router1
Router1(config)#end
Router1#
```

>**NOTE** - If you see a "Configured from console by console" message appear, review the exercise, [Set up the logging process for the device](#set-up-the-logging-process-for-the-device "Set up the logging process for the device").

However, we like ```R1```, so change it back:

```
configure terminal
hostname R1
end
```

You should start and end in Privileged EXEC Mode after each change.

Go back to your **Python Terminal** and enter the following commands:

```
child.sendline('configure terminal\r')
child.expect_exact('R2(config)#')
child.sendline('hostname Router2\r')
child.expect_exact('Router2(config)#')
child.sendline('end\r')
child.expect_exact('Router2#')
child.sendline('configure terminal\r')
child.expect_exact('Router2(config)#')
child.sendline('hostname R2\r')
child.expect_exact('R2(config)#')
child.sendline('end\r')
child.expect_exact('R2#')
```

Check your output for errors. A ```0``` should appear after you enter the last line, which indicates that the child process is back at the Privileged EXEC Mode prompt.

-----

## Update the startup configuration of the device

When we make changes to the device, such as changing the hostname, we are making changes to the ***running configuration***; everything will return to its default values when the device reloads. To make the changes permanent, you must copy the running configuration, held in the device's volatile random-access memory (RAM), to the device's ***startup configuration***, stored in its nonvolatile RAM (NVRAM).

Even though we rolled-back our changes, go back to your **Console Terminal** and make the current configuration the default configuration:

```
copy running-config startup-config ; or copy run start
```

The device will prompt you for a ```Destination filename```, with ```startup-config``` as the default. You can re-enter "startup-config", or you can just press <kbd>Enter</kbd> to accept the default value.

**Output:**

```
R1#copy running-config startup-config
Destination filename [startup-config]? 
Building configuration...
[OK]
R1#
```

Go back to your **Python Terminal** and enter the following commands:

```
child.sendline('copy running-config startup-config\r')
index = child.expect_exact(['Destination filename', 'R2#', ])
if index == 0:
    child.sendline('startup-config\r')
    child.expect_exact('[OK]')
    child.expect_exact('R2#')  # After this line, press Enter again to exit if-else mode
```

Check your output for errors. A ```0``` should appear after you enter the last line, which indicates that the child process is back at the Privileged EXEC Mode prompt.

-----

## Identify the default file system of the device

Cisco devices have default file systems, where files are read and copied to and from, if no other file system is identified. They also store system images, configuration files, and more. However, depending on the device, the name of the default file system may be ```flash```, ```flash0```, ```bootflash```, ```slot0```, etc. Knowing the name of the default file system is important; you do not want to copy files to the wrong directory!

Go back to your **Console Terminal** and get a list of the device's file systems:

```
show file systems
```

**Output:**

```
File Systems:

     Size(b)     Free(b)      Type  Flags  Prefixes
      155640      153658     nvram     rw   nvram:
*  134182912    67104768      disk     rw   flash:
```

The asterisk (```*```) indicates the current file system, while the ```Prefixes``` provide the names of the file systems.

Verify the name of the default file system and look at its contents:

```
dir
```

**Output:**

```
R1#dir
Directory of flash:/

No files in directory

134182912 bytes total (67104768 bytes free)
R1#
```

The device's default file system is ```flash```. 

>**NOTE** - If the message, ```PCMCIA disk 0 is formatted from a different router or PC. A format in this router is required before an image can be booted from this device```, appears, this means that the file system is not formatted. That's OK; we will learn how to format a file system after this exercise.

Go back to your **Python Terminal** and enter the following commands:

```
child.sendline('show file systems\r')
child.expect_exact('R2#')
print(child.before)
child.sendline('dir\r')
child.expect_exact('dir')
index = child.expect_exact(['More', 'R2#', ])
dir_list = str(child.before)
if index == 0:
    # No need to get the whole directory listing, so break out
    child.sendcontrol('c')
    child.expect_exact('R2#')  # After this line, press Enter again to exit if-else mode

default_file_system = dir_list.split('Directory of ')[1].split(':')[0].strip()
if not default_file_system.startswith(('bootflash', 'flash', 'slot', 'disk',)):
    raise RuntimeError('Cannot get the device\'s working drive.')  # After this line, press Enter again to exit if-else mode

# If the drive is not formatted, a warning will appear, followed by another prompt.
# Wait for it to pass, and get to the correct prompt
index = child.expect_exact(['before an image can be booted from this device', pexpect.TIMEOUT, ], timeout=5)
if index == 0:
    child.expect_exact('R2#')  # After this line, press Enter again to exit if-else mode
```

Check your output for errors. A ```0``` should appear after you enter the last line, which indicates that the child process is back at the Privileged EXEC Mode prompt.

-----

## Get the name of the device

There are several ways to get the name of a Cisco device, but for the Cisco 3745 router, the best way is to look for the product number of the first field replaceable unit (FRU).

Go back to your **Console Terminal** and enter the following commands:

```
show diag | include FRU
show tech-support | include FRU
```

**Output:**

```
R1#show diag | include FRU
	Product (FRU) Number     : C3745-2FE
R1#show tech-support | include FRU
	Product (FRU) Number     : C3745-2FE
```

The second command takes longer, since the ```tech-support``` "dump" contains a lot of additional information about the device (e.g., the startup configuration, the status of the ports, etc.) 

Go back to your **Python Terminal** and enter the following commands:

```
import re
try:
    child.sendline('show diag | include FRU\r')
    child.expect_exact('R2#')
    device_name = str(child.before).split('show diag | include FRU\r')[1].splitlines()[1].strip()
    if not re.compile(r'Product \(FRU\) Number').search(device_name):
        raise RuntimeError('Cannot get the device\'s name.')
except (RuntimeError, IndexError) as ex:
    device_name = None  # After this line, press Enter again to exit try-expect mode

print(device_name)
```

Check your output for errors. A ```0``` should appear after you enter the last line, which indicates that the child process is back at the Privileged EXEC Mode prompt.

-----

## Get the serial number of the device

There are several ways to get the serial number of a Cisco device, but for the Cisco 3745 router, the best way is to look for identification number of the processor board.

Go back to your **Console Terminal** and enter the following commands:

```
show version | include [Pp]rocessor [Bb]oard [IDid]
show tech-support | include [Pp]rocessor [Bb]oard [IDid]
```

**Output:**

```
R1#show version | include [Pp]rocessor [Bb]oard [IDid]
Processor board ID FTX0945W0MY
R1#show tech-support | include [Pp]rocessor [Bb]oard [IDid]   
Processor board ID FTX0945W0MY
```

The second command takes longer, since the ```tech-support``` "dump" contains a lot of additional information about the device (e.g., the startup configuration, the status of the ports, etc.) 

Go back to your **Python Terminal** and enter the following commands:

```
import re
try:
    child.sendline('show version | include [Pp]rocessor [Bb]oard [IDid]\r')
    child.expect_exact('R2#')
    serial_num = str(child.before).split('show version | include [Pp]rocessor [Bb]oard [IDid]\r')[1].splitlines()[1].strip()
    if not re.compile(r'[Pp]rocessor [Bb]oard [IDid]').search(serial_num):
        raise RuntimeError('Cannot get the device\'s serial number.')
except (RuntimeError, IndexError) as ex:
    serial_num = None  # After this line, press Enter again to exit try-expect mode

print(serial_num)
```

Check your output for errors. A ```0``` should appear after you enter the last line, which indicates that the child process is back at the Privileged EXEC Mode prompt.

-----

## Get the operating system version of the device

There are several ways to get the operating system's name and version of a Cisco device.

Go back to your **Console Terminal** and enter the following commands:

```
show version | include [IOSios] [Ss]oftware
show tech-support | include [IOSios] [Ss]oftware
```

**Output:**

```
R1#show version | include [IOSios] [Ss]oftware
Cisco IOS Software, 3700 Software (C3745-ADVENTERPRISEK9-M), Version 12.4(25d), RELEASE SOFTWARE (fc1)
R1#show tech-support | include [IOSios] [Ss]oftware
Cisco IOS Software, 3700 Software (C3745-ADVENTERPRISEK9-M), Version 12.4(25d), RELEASE SOFTWARE (fc1)
```

The second command takes longer, since the ```tech-support``` "dump" contains a lot of additional information about the device (e.g., the startup configuration, the status of the ports, etc.) 

Go back to your **Python Terminal** and enter the following commands:

```
import re
try:
    child.sendline('show version | include [IOSios] [Ss]oftware\r')
    child.expect_exact('R2#')
    software_ver = str(child.before).split('show version | include [IOSios] [Ss]oftware\r')[1].splitlines()[1].strip()
    if not re.compile(r'[IOSios] [Ss]oftware').search(software_ver):
        raise RuntimeError('Cannot get the device\'s software version.')
except (RuntimeError, IndexError) as ex:
    software_ver = None  # After this line, press Enter again to exit try-expect mode

print(software_ver)
```

Check your output for errors. A ```0``` should appear after you enter the last line, which indicates that the child process is back at the Privileged EXEC Mode prompt.

-----

## Format a file system on the device

Go back to your **Console Terminal** and look at your log:

```
show logging
```

>**NOTE** - After entering the ```show logging``` command, you may see ```--More--``` appear at the bottom of the listing, which means that there is more text to follow. Press <kbd>Space</kbd> to continue reading the log until the ```R1#``` prompt appears again. By the way, pressing <kbd>Enter</kbd> will only advance the log one entry at a time.

You should see an entry, similar to the following:

```
*Mar  1 00:00:05.239: %PCMCIAFS-5-DIBERR: PCMCIA disk 0 is formatted from a different router or PC. A format in this router is required before an image can be booted from this device
```

This entry tells you that the device's default file system is not formatted, which means that you will be unable to save files on the device. While it is unusual for a new device to ship without a formatted default file system, it can occur, and you may also have to format replacement drives and cards.

Earlier, you looked up the name of the default file system (i.e., ```flash```). Format the drive, using the following command, and press <kbd>Enter</kbd> each time you are asked to ```confirm```:

```
format flash:
```

**Output:**

```
R1#format flash:
Format operation may take a while. Continue? [confirm]
Format operation will destroy all data in "flash:".  Continue? [confirm]
Format: Drive communication & 1st Sector Write OK...
Writing Monlib sectors.
.........................................................................................................................
Monlib write complete 

Format: All system sectors written. OK...

Format: Total sectors in formatted partition: 130911
Format: Total bytes in formatted partition: 67026432
Format: Operation completed successfully.

Format of flash complete
```

If you look at the contents of the ```flash``` file system, you will see it is empty and that all its memory is available for storage:

```
show flash:
```

**Output:**

```
R1#show flash:
No files on device

66875392 bytes available (0 bytes used)
```

Go back to your **Python Terminal** and enter the following commands:

```
child.sendline('format flash:\r')
index = 1
while index != 0:
    index = child.expect_exact([pexpect.TIMEOUT, 'Continue? [confirm]', 'Enter volume ID', ], timeout=5)
    if index != 0:
        child.sendline('\r')  # After this line, press Enter again to exit while mode

child.expect_exact('Format of flash complete', timeout=120)
child.sendline('show flash:\r')
child.expect_exact('(0 bytes used)')
child.expect_exact('R2#')
```

Check your output for errors. A ```0``` should appear after you enter the last line, which indicates that the child process is back at the Privileged EXEC Mode prompt.

-----

## Assign the router an IPv4 address

Go back to your **Console Terminal** and look at the configuration of your network interfaces:

```
show ip interface brief
```

**Output:**

```
R1#show ip interface brief
Interface                  IP-Address      OK? Method Status                Protocol
FastEthernet0/0            unassigned      YES NVRAM  administratively down down    
FastEthernet0/1            unassigned      YES NVRAM  administratively down down    
```

While your device is a Layer 3 device, none of its interfaces have an IPv4 or IPv6 address. Without an IP address, you cannot perform tasks over Ethernet, such as using Secure Shell (SSH) or uploading a configuration. Of course, you can transfer files through the console port, using an [XMODEM](https://en.wikipedia.org/wiki/XMODEM "XMODEM") protocol utility, but, trust me, uploading and downloading files through an Ethernet port is much faster and easier.

Assign the first built-in Ethernet port, ```FastEthernet0/0```, an IPv4 address:

```
configure terminal
interface FastEthernet0/0
ip address 192.168.1.20 255.255.255.0
no shutdown
end
```

Check your interfaces again, and you should see that ```FastEthernet0/0``` is now configured:

**Output:**

```
R1#show ip interface brief
Interface                  IP-Address      OK? Method Status                Protocol
FastEthernet0/0            192.168.1.20    YES manual up                    up      
FastEthernet0/1            unassigned      YES NVRAM  administratively down down    
```

Make the changes permanent by following the instructions in the [Update the startup configuration of the device](#update-the-startup-configuration-of-the-device "Update the startup configuration of the device") exercise.

Go back to your **Python Terminal** and enter the following commands:

>**NOTE** - ***IMPORTANT!** The IPv4 address of **R1** is **192.168.1.20**, and the IPv4 address of **R2** will be **192.168.1.30**!*

```
child.sendline('configure terminal\r')
child.expect_exact('R2(config)#')
child.sendline('interface FastEthernet0/0\r')
child.expect_exact('R2(config-if)#')
child.sendline('ip address 192.168.1.30 255.255.255.0\r')
child.expect_exact('R2(config-if)#')
child.sendline('no shutdown\r')
child.expect_exact('R2(config-if)#')
child.sendline('end\r')
child.expect_exact('R2#')
```

Check your output for errors. A ```0``` should appear after you enter the last line, which indicates that the child process is back at the Privileged EXEC Mode prompt.

Once again, Make the changes permanent by following the instructions in the [Update the startup configuration of the device](#update-the-startup-configuration-of-the-device "Update the startup configuration of the device") exercise.

-----

## Test connectivity from the device to the host

Before performing any tasks over Ethernet, such as using Secure Shell (SSH) or uploading a configuration, you should check the connection to your source or destination. The Cisco IOS has a version of the [ping utility](https://en.wikipedia.org/wiki/Ping_(networking_utility) "Ping (networking utility)") that you can use to check your connections.

Go back to your **Console Terminal** and check the device's connection to the host:

>**NOTE** - By default, Cisco's ping only sends 5 Internet Control Message Protocol (ICMP) echo requests. To change the number of packets you want to send, add the ```repeat``` keyword after the IPv4 address (e.g., ```ping 192.168.1.10 repeat 10```).

```
ping 192.168.1.10
```

**Output:**

```
R1#ping 192.168.1.10 

Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 192.168.1.10, timeout is 2 seconds:
.!!!!
Success rate is 80 percent (4/5), round-trip min/avg/max = 8/10/12 ms
```

Go back to your **Python Terminal** and enter the following commands:

```
child.sendline('ping 192.168.1.10\r')
index = child.expect(['Success rate is 0 percent', 'R2#', ], timeout=60)
if index == 0:
    raise RuntimeError('Cannot ping the host from this device.')  # After this line, press Enter again to exit while mode

print(child.before)
```

Check your output for errors. You should see results similar to the manual method results.

-----

## Test connectivity from the host to the device

Up to this point, you have only used CentOS' Bourne-again Shell (Bash) to either connect to a device using Telnet or to open a Python interpreter. To perform tasks over Ethernet, such as using Secure Shell (SSH) or uploading a configuration, you will have to start and stop Linux services, run Linux utilities, etc., on the host device using Bash.

Open another Terminal and enter the following command; this will be your **Bash Terminal**:

```
ping -c 4 192.168.1.20
```

**Output:**

```
[gns3user@localhost ~]$ ping -c 4 192.168.1.20
PING 192.168.1.20 (192.168.1.20) 56(84) bytes of data.
64 bytes from 192.168.1.20: icmp_seq=1 ttl=255 time=27.0 ms
64 bytes from 192.168.1.20: icmp_seq=2 ttl=255 time=8.31 ms
64 bytes from 192.168.1.20: icmp_seq=3 ttl=255 time=8.37 ms
64 bytes from 192.168.1.20: icmp_seq=4 ttl=255 time=8.37 ms

--- 192.168.1.20 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3005ms
rtt min/avg/max/mdev = 8.315/13.020/27.012/8.078 ms
```

Go back to your **Python Terminal**. Your child process is running Telnet; it cannot run Bash at the same time. We have two choices: we can create a new Bash child process, or we can use Pexpect's ```run``` command. A child process is overkill for conducting a "ping"; use Pexpect's ```run``` command instead:

```
command_output, exitstatus = pexpect.run('ping -c 4 192.168.1.30', withexitstatus=True)
if exitstatus != 0:
    raise RuntimeError('Unable to ping device: {0}'.format(command_output))  # After this line, press Enter again to exit while mode

print(command_output)
```

Check your output for errors. A ```0``` should appear after you enter the last line, which indicates that the child process is back at the Privileged EXEC Mode prompt.

-----

## Secure the console and auxiliary ports

Go back to your **Console Terminal** and look at your startup configuration:

```show startup-config```

Near the end, you should see the following lines:

**Output:**

```
line con 0
 exec-timeout 0 0
 logging synchronous
 privilege level 15
 no login
line aux 0
 exec-timeout 0 0
 logging synchronous
 privilege level 15
 no login 
```

The ```exec-timeout 0 0``` line means that connections over the console and auxiliary ports will not time out and close. The ```logging synchronous``` line means that console messages will not suddenly appear in the middle of a command. Instead, console messages will end with a new prompt (which you corrected in the [Set up the logging process for the device](#set-up-the-logging-process-for-the-device "Set up the logging process for the device") exercise).

While not setting a session time limit is dangerous, the last two lines, ```privilege level 15``` and ```no login```, can cause even worse problems. The ```privilege level 15``` line means that whoever connects to the device through the console or auxiliary ports will have full access to the device's commands, including reading and writing configuration files.

>**NOTE** - Cisco devices have 16 privilege levels (0 through 15). 13 are customizable, while three are set by the IOS:
>
>- 0 - No privileges
>- 1 - Read-only and access to the ping command
>- 15 - Full access, including reading and writing configuration files
>
>To see your privilege level, enter ```show privilege``` at the prompt.

The ```no login``` line means that the device requires no username or password for connections through the console or auxiliary port. While this setting makes it easy for network engineers to troubleshoot a device, it also makes it easy for bad actors to hack the device, if they could access either port.

>**NOTE** - The ```no login``` line may not appear. However, both cases have the same effect: ```no login``` explicitly states that no password is required, while a missing line does the same implicitly. 

Secure both ports by entering the following commands:

```
configure terminal ; Enter Global Configuration Mode
line console 0 ; Enter Line Configuration Mode for the console port
exec-timeout 30 0 ; Timeout connection after 30 minutes
password ciscon
login ; Require a password when connecting to the console port
exit ; Return to Global Configuration Mode
line aux 0 ; Enter Line Configuration Mode for the auxiliary port
exec-timeout 30 0 ; Timeout connection after 30 minutes
password cisaux
login ; Require a password when connecting to auxiliary port
end
```

>**NOTE:** 
>- In real life, make sure you use better passwords.
>- The maximum length for a Cisco password is **64** characters.
>- Never add comments after a Cisco password; they will be included in the password.
>- Check out [xkcd's take on passwords](https://xkcd.com/936/ "xkcd:Password Strength").

Make the changes permanent by following the instructions in the [Update the startup configuration of the device](#update-the-startup-configuration-of-the-device "Update the startup configuration of the device") exercise.

Press <kbd>Ctrl</kbd> + <kbd>]</kbd>, then enter "q" at the ```telnet>``` prompt, to exit Telnet. Once you have exited Telnet, go to the GNS3 GUI. Right-click on the device, and select **Stop**, then **Reload**.

Reconnect to the device through Telnet:

```telnet 192.168.1.1 5001```

>**NOTE** - If the device asks you to ```Press RETURN to get started!```, press <kbd>Enter</kbd> to continue. 

**Output:**

```
User Access Verification

Password:
```

Enter your password (```ciscon```). The Privileged EXEC mode prompt (```R1#```) should appear.

Before continuing to the Python script, look at the console and auxiliary port passwords in ```startup-config```:

```
show startup-config | include [Pp]assword
```

**Output:**

```
R1#show startup-config | include [Pp]assword
no service password-encryption
 password ciscon
 password cisaux
```

The passwords are in plain text! The good news is that, for the console and auxiliary passwords, Cisco has a built-in password encryption service that uses a reversible Vigenère cipher, which generates a 14-character alphanumeric string. While this is not as secure as using a one-way hashing algorithm, it will protect the passwords from prying eyes. 

Encrypt the passwords by enabling the password encryption service:

```
configure terminal
service password-encryption
end
```

Make the changes permanent by following the instructions in the [Update the startup configuration of the device](#update-the-startup-configuration-of-the-device "Update the startup configuration of the device") exercise.

Look at the console and auxiliary port passwords in ```startup-config``` again:

```
show startup-config | include [Pp]assword
```

**Output:**

```
R1#show startup-config | include [Pp]assword
service password-encryption
 password 7 104D000A06181C
 password 7 104D000A04020A
```

Great! The passwords are no longer in plain text.

>**NOTE** - The ```7``` after ```password``` indicates how the following text was encrypted. Here are all the codes:
>- ```0``` - No encryption
>- ```4``` - Secure Hash Algorithm-256 (SHA-256) without salting
>- ```5``` - Message Digest 5 (MD5) hashing algorithm with salting
>- ```7``` - Vigenère cipher
>- ```8``` - Password-Based Key Derivation Function 2 (PBKDF2) with salting (only available for IOS 15.3+)

Go back to your **Python Terminal** and enter the following commands:

```
child.sendline('configure terminal\r')
child.expect_exact('R2(config)#')
child.sendline('service password-encryption\r')
child.expect_exact('R2(config)#')
child.sendline('line console 0\r')
child.expect_exact('R2(config-line)#')
child.sendline('password ciscon\r')
child.expect_exact('R2(config-line)#')
child.sendline('login\r')
child.expect_exact('R2(config-line)#')
child.sendline('exit\r')
child.expect_exact('R2(config)#')
child.sendline('line aux 0\r')
child.expect_exact('R2(config-line)#')
child.sendline('password cisaux\r')
child.expect_exact('R2(config-line)#')
child.sendline('login\r')
child.expect_exact('R2(config-line)#')
child.sendline('end\r')
child.expect_exact('R2#')
```

Check your output for errors. A ```0``` should appear after you enter the last line, which indicates that the child process is back at the Privileged EXEC Mode prompt.

Once again, make the changes permanent by following the instructions in the [Update the startup configuration of the device](#update-the-startup-configuration-of-the-device "Update the startup configuration of the device") exercise.

Next, close the connection to the device:

```
child.close()
```

Go to the GNS3 GUI. Right-click on the device, and select **Stop**, then **Reload**.

Reconnect to the device through Telnet:

```
child = pexpect.spawn('telnet 192.168.1.30')
child.sendline('\r')
# Increase the timeout to allow the device to boot up
child.expect_exact('Password:', timeout=300)
child.sendline('ciscon\r')
child.expect_exact('R2#')
```

Check your output for errors. A ```0``` should appear after you enter the last line, which indicates that the child process is back at the Privileged EXEC Mode prompt.

-----

## Secure the Privileged EXEC Mode

Go back to your **Console Terminal** and exit and re-enter Privileged EXEC Mode:

```
disable
enable
```

**Output:**

```
R1#disable
R1>enable
R1#
```

The device did not ask you for a password. This means that anyone can elevate from User EXEC Mode and basic access (Privilege Level 0) to Privileged EXEC Mode and full access (Privilege Level 15), without authentication.

This is not good. Secure the device's Privileged EXEC Mode:

```
configure terminal
enable password cisen
end ; Secure and return to Privileged EXEC Mode
```

>**NOTE:** 
>- In real life, make sure you use better passwords.
>- The maximum length for a Cisco password is **64** characters.
>- Never add comments after a Cisco password; they will be included in the password.
>- Check out [xkcd's take on passwords](https://xkcd.com/936/ "xkcd:Password Strength").

Make the changes permanent by following the instructions in the [Update the startup configuration of the device](#update-the-startup-configuration-of-the-device "Update the startup configuration of the device") exercise.

Now, try to exit and re-enter Privileged EXEC Mode:

**Output:**

```
R1#disable
R1>enable
Password:
```

Enter your password (```cisen```). The Privileged EXEC mode prompt (```R1#```) should appear.

Before continuing to the Python script, look at the Privileged EXEC mode password in ```startup-config```:

```
show startup-config | include [Ee]nable
```

**Output:**

```
R1#show startup-config | include [Ee]nable  
enable password 7 05080F1C2442
```

Great! The Privileged EXEC mode password uses the same Vigenère cipher encryption service as the console and auxiliary passwords. Since you already enabled the service, the password is encrypted.

Go back to your **Python Terminal** and enter the following commands:

```
child.sendline('configure terminal\r')
child.expect_exact('R2(config)#')
child.sendline('service password-encryption\r')
child.expect_exact('R2(config)#')
child.sendline('enable password cisen\r')
child.sendline('end\r')
child.expect_exact('R2#')
```

Check your output for errors. A ```0``` should appear after you enter the last line, which indicates that the child process is back at the Privileged EXEC Mode prompt.

Once again, make the changes permanent by following the instructions in the [Update the startup configuration of the device](#update-the-startup-configuration-of-the-device "Update the startup configuration of the device") exercise.

-----

## Secure the virtual teletype (VTY) lines

Go back to your **Console Terminal**. Press <kbd>Ctrl</kbd> + <kbd>]</kbd>, then enter "q" at the ```telnet>``` prompt, to exit Telnet.

**Output:**

```
R1#
telnet> q
Connection closed.
[gns3user@localhost ~]$
```

Attempt to Telnet into the device using the IPv4 address you assigned to **R1**:

```telnet 192.168.1.20```

**Output:**

```
Trying 192.168.1.20...
Connected to 192.168.1.20.
Escape character is '^]'.

Password required, but none set
Connection closed by foreign host.
```

![Whaaat?](../img/whaaat.gif "Whaaat?")

What happened? Well, when you saved the changes to ```FastEthernet0/0```, the device added this line to the end of the startup configuration:

```
line vty 0 4
 login
```

The Cisco 3745 router has five virtual teletype (VTY) lines (0 through 5). As a fail-safe, the device requires a login whenever a user attempts to access it through a VTY line, as you just attempted to do. The problem is that you never set a password for the VTY line, so the device cannot let you in. 

You have several options. 

1. One way is to continue connecting through the console port, but our goal is to automate tasks, such as IOS updates and reconfigurations, and perform them remotely. In addition, imagine you had to update the devices in each cabinet for a data center with 100+ cabinets, all through the console port; it would take a long time. 
2. Another way is to change the configuration, by replacing ```login``` with ```no login```, removing the authentication requirement.
3. However, the best option is to secure the lines; whenever you can, "err" on the side of security.

Telnet back into the device through the console port:

```telnet 192.168.1.1 5001```

Now you will secure the VTY line. Set the username to ```admin```, the privilege level to "15", and the password to ```cisco```:

```
configure terminal
; Secure the VTY lines and return to Global Configuration Mode
username admin privilege 15 password cisco
line vty 0 4 ; Enter Line Configuration Mode for VTY
login local ; See the note below
end
```

>**NOTE** - Since you identified a user (```username admin```), you must require a ```local``` username when logging in remotely. You can leave out the username (e.g., ```privilege 15 password cisco```), but you would not be able to keep track of who used the device. As we said before, "err" on the side of security.

>**NOTE:** 
>- In real life, make sure you use better passwords.
>- The maximum length for a Cisco password is **64** characters.
>- Never add comments after a Cisco password; they will be included in the password.
>- Check out [xkcd's take on passwords](https://xkcd.com/936/ "xkcd:Password Strength").

Make the changes permanent by following the instructions in the [Update the startup configuration of the device](#update-the-startup-configuration-of-the-device "Update the startup configuration of the device") exercise.

Press <kbd>Ctrl</kbd> + <kbd>]</kbd>, then enter "q" at the ```telnet>``` prompt, to exit Telnet.

Once again, attempt to Telnet into the device using the IPv4 address you assigned to **R1**:

```telnet 192.168.1.20```

**Output:**

```
Trying 192.168.1.20...
Connected to 192.168.1.20.
Escape character is '^]'.


User Access Verification

Username:
```

Enter your username (```admin```). When prompted, enter your password (```cisco```). The Privileged EXEC mode prompt (```R1#```) should appear.

Before continuing to the Python script, look at the VTY password in ```startup-config```:

```
show startup-config | include [Uu]sername
```

**Output:**

```
R1#show startup-config | include username   
username admin privilege 15 password 7 02050D480809
```

The password is encrypted using the reversible Vigenère cipher encryption service you enabled earlier. However, for VTY lines, you can use the device's MD5 hash generator, which also "salts" the text, resulting in a more secure 30-character string.

Fix the VTY password by removing the cipher text and replacing it with a hashed password:

```
configure terminal
no username admin password cisco
username admin privilege 15 secret cisco
end
```

Make the changes permanent by following the instructions in the [Update the startup configuration of the device](#update-the-startup-configuration-of-the-device "Update the startup configuration of the device") exercise.

Look at the password in ```startup-config``` again:

```
show startup-config | include [Uu]sername
```

**Output:**

```
R1#show startup-config | include [Uu]sername 
username admin privilege 15 secret 5 $1$x5XQ$hk/6IMVA./RsstlqrA/iu/
```

Great! The remote password is hashed. If you would like to verify that all the passwords and secrets are encrypted:

```
R1#show startup-config | include [Pp]assword|[Ss]ecret  
service password-encryption
enable password 7 05080F1C2442
username admin privilege 15 secret 5 $1$x5XQ$hk/6IMVA./RsstlqrA/iu/
 password 7 104D000A06181C
 password 7 104D000A04020A
```

Go back to your **Python Terminal** and enter the following commands:

>**NOTE** - ***IMPORTANT!** The IPv4 address of **R1** is **192.168.1.20**, and the IPv4 address of **R2** will be **192.168.1.30**!*

```
child.sendline('configure terminal\r')
child.expect_exact('R2(config)#')
child.sendline('username admin privilege 15 secret cisco\r')
child.expect_exact('R2(config)#')
child.sendline('line vty 0 4\r')
child.expect_exact('R2(config-line)#')
child.sendline('login local\r')
child.expect_exact('R2(config-line)#')
child.sendline('end\r')
child.expect_exact('R2#')

# Close the console port connection and Telnet through FastEthernet0/0
child.close()
child = pexpect.spawn('telnet 192.168.1.30')
# Increase the timeout to allow the device to boot up
child.expect_exact('Username:', timeout=300)
# DO NOT ADD A CARRIAGE RETURN FOR THE USERNAME AND PASSWORD
child.sendline('admin')
child.expect_exact('Password:')
child.sendline('cisco')
child.expect_exact('R2#')
```

Check your output for errors. A ```0``` should appear after you enter the last line, which indicates that the child process is back at the Privileged EXEC Mode prompt.

Once again, make the changes permanent by following the instructions in the [Update the startup configuration of the device](#update-the-startup-configuration-of-the-device "Update the startup configuration of the device") exercise.

>**NOTE** - ***IMPORTANT!** Do not append a carriage return (```\r```) to commands when connected through a VTY line! Review the EOL explanation in the [Access the Privileged EXEC mode of the device](#access-the-privileged-exec-mode-of-the-device "Access the Privileged EXEC mode of the device")* exercise.

>**NOTE** - By default, connections to the VTY lines will time out after 10 minutes. This means that, between exercises, you may see this message:
>
>```Connection closed by foreign host.```
>
>If you like, you can change the timeout value. For example, if you want to change it to 1 hour and 15 seconds:
>
>```
>configure terminal
>line vty 0 4
>exec-timeout 60 15
>end
>```
>
>The Python code is as follows:
>
>```
>child.sendline('configure terminal\r')
>child.expect_exact('R2(config)#')
>child.sendline('line vty 0 4\r')
>child.expect_exact('R2(config-line)#')
>child.sendline('exec-timeout 60 30\r')
>child.expect_exact('R2(config-line)#')
>child.sendline('end\r')
>child.expect_exact('R2#')
>```

-----

## Set the device clock manually

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Enable the NTP server on the host

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Update the device clock using the host NTP server

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Enable secure communications with the device

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Connect to the device from the host via Secure Shell (SSH)

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Enable the TFTP server on the host

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Download the device startup configuration to the host via TFTP

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Determine and display the hash value of a file

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Upload a non-existing file from the host to the device via TFTP

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Download a non-existing file from the host to the device via TFTP

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Upload an existing file from the host to the device via TFTP

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Download an existing file from the host to the device via TFTP

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Enable the FTP server on the host

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Prepare the device for FTP transfers

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Download the device startup configuration to the host via FTP

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Upload a non-existing file from the host to the device via FTP

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Download a non-existing file from the host to the device via FTP

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Upload an existing file from the host to the device via FTP

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Download an existing file from the host to the device via FTP

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Enable the SCP server on the host

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Download the device startup configuration to the host via SCP

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Upload a non-existing file from the host to the device via SCP

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Download a non-existing file from the host to the device via SCP

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Upload an existing file from the host to the device via SCP

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Download an existing file from the host to the device via SCP

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Reload the device

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Disable the TFTP service on the host

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Disable the FTP service on the host

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Disable the NTP service on the host

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Disable the SCP service on the host (optional)

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

-----

## Congratulations!

Nicely done! You should now have a good idea on how to perform common networking tasks through the Cisco command-line interface (CLI), and how to automate those tasks in Python using Pexpect.
