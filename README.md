# Adventures in Network Automation

***Disclaimer: Many experts (and the creators of GNS3 themselves) no longer recommend using Dynamips' Cisco IOS images, since the devices that use those images are no longer supported by Cisco. They recommend using more up-to-date images, such as QEMU or those available through Cisco's Virtual Internet Routing Lab (VIRL). However, since this tutorial is only a general introduction to automating network device configuration using Python, we will use the freely-available Dynamips images.***

***In addition, Cisco Packet Tracer, while an excellent tool, is not suitable for our purposes, since it cannot interact with its host or integrated development environments (IDEs).***

## Introduction

Recently, for personal and professional reasons (CompTIA, anyone?), I've delved into programming networking devices from within and without. Normally, in order to interact with a device like a switch, you must connect to it physically, via a serial or Ethernet cable, access its command-line interface (CLI), and enter commands manually or upload a script, usually written in Cisco's Tool Command Language (TCL).

This is fine if you have one switch or router, but if you have dozens or hundreds of devices, this can become a full-time job. Wouldn't it be easier to write an application, let's say in Python, that can connect to a device; upload a configuration; reboot the device; and then test the device to ensure it is properly configured? The answer is yes; you can write such a script, especially with Python, using modules such as subprocess and pexpect.

The bad news is that to test the program, you will still need a physical device. You just can't download an Internetwork Operating System (IOS) image, and then interact with it using a hypervisor like VirtualBox. However, there are some great tools, like the Graphical Network Simulator-3 (GNS3), which can virtualize IOS images, and, with a little tweaking, can let you test your code against a network device.

This tutorial is broken down into three parts:

- [Installing GNS3](#installing-gns3 "Installing GNS3")
- [Setting up the environment](#setting-up-the-environment "Setting up the environment")
- [Running the Labs](#running-the-labs "Running the Labs")

Many thanks to David Bombal, Paul Browning, and many other incredible coders and network gurus (you know who you are :thumbsup:).

-----

## Installing GNS3

### Linux

Setting up GNS3 in Ubuntu and Debian is pretty simple: check out [https://docs.gns3.com/docs/getting-started/installation/linux](https://docs.gns3.com/docs/getting-started/installation/linux "GNS3 Linux Install").

However, GNS3 doesn't work straight-out-of-the-box with Fedora, Red Hat Linux (RHEL), and CentOS. But before kicking them to the curb, remember...

1. Approximately [20% of servers running Linux](https://w3techs.com/technologies/details/os-linux "Usage statistics of Linux for websites") use one of these operating systems, and RHEL is second, behind Microsoft, in [paid enterprise OS subscriptions](https://www.idc.com/getdoc.jsp?containerId=US46684720 "Worldwide Server Operating Environments Market Shares, 2019").

2. Many companies and government agencies, such as NASA and the DOD, use Red Hat Linux (i.e., the "commercial" version of CentOS), since it is a trusted OS which is [Protection Profile (PP) compliant](https://www.commoncriteriaportal.org/products/ "Certified Common Criteria Products").

We used Centos 7 for the labs and demos in this repository. While there were a lot of good posts and articles on how to install GNS3 on CentOS, each of them were slightly different, so we distilled them into [one shell script](gns3_setup_centos.sh "CentOS Setup Script"). To run this script, make sure you assign executable permissions to the file first (i.e., "chmod +x [gns3_setup_centos.sh](gns3_setup_centos.sh "CentOS Setup Script")). We also recommend you look at the comments in the script, so you can become familiar with GNS3's dependencies.

### Windows

Installing GNS3 on windows is also relatively simple; check out [https://docs.gns3.com/docs/getting-started/installation/windows/](https://docs.gns3.com/docs/getting-started/installation/windows/ "GNS3 Windows Install"). David Bombal also has a [great video sereis on using GNS3](https://www.youtube.com/watch?v=Ibe3hgP8gCA&list=PLhfrWIlLOoKNFP_e5xcx5e2GDJIgk3ep6&index=1&ab_channel=DavidBombal "GNS3 Installation - David Bombal"), starting with installation; highly recommended!

-----

## Setting up the environment

In order for your code to interact with the switch, you will need to connect your host computer with virtual devices in GNS3. To do so in Windows, you will need to create a Loopback interface. To do so in Linux, you will need to create a TUN/TAP interface.

Before we start, here's the subnet info for the network:

- **Network Address: 192.168.1.0/24**
- **Subnet Mask: 255.255.255.0 (ff:ff:ff:00)**
- Total Number of Hosts: 256
- Number of Usable Hosts: 254
- Usable IP Range: 192.168.1.1 - 192.168.1.254
- **GNS3 Host Device IP Address: 192.168.1.1/32**
- **First Virtual Device IP Address: 192.168.1.10/32**
- Gateway: 192.168.1.254
- Broadcast Address: 192.168.1.255
- Wildcard Mask: 0.0.0.255
- Binary Subnet Mask: 11111111.11111111.11111111.00000000
- IP Class and Type: C (Private)
- CIDR Notation: /24
- Binary TCP/IP Address: 11000000101010000000000100000001
- Decimal TCP/IP Address: 3232235777
- Hexadecimal TCP/IP Address: 0xc0a80101
- in-addr.arpa: 1.1.168.192.in-addr.arpa
- IPv4 Mapped Address: ::ffff:c0a8.0101
- 6to4 Prefix: 2002:c0a8.0101::/48

### Linux

In gns3_setup_centos.sh, you installed bridge-utils, a utility which creates and manages Ethernet bridge devices. We will use this bridge to connect the host machine and GNS3 virtual devices.

The gns3_run.sh script sets up your environment, runs GNS3, and resets your environment when you exit GNS3. Please open the gns3_run.sh file and examine it. This script does the following:

1. Identifies the Ethernet interface and its IP address (if assigned).
2. Creates a network TAP interface: GNS3 devices will connect to this interface. By the way, ```ethtool -i tap0``` and ```ip link show type tap``` will both report the tap (Layer 2) is a tun (Layer 3), but ```ip tuntap show``` will report the interface correctly as a tap. Check out [Paul Gorman's Linux Bridges and Virtual Networking](https://paulgorman.org/technical/linux-bridges-and-virtual-networking.txt.html "Paul Gorman's Linux Bridges and Virtual Networking") for more details.
3. Creates a network bridge that connects the host machine to the tap interface.
4. Starts GNS3.

>**NOTE** - You will not be able to connect to the Internet through your Ethernet interface until you exit GNS3

When you exit GNS3, the script will close the bridge and tap, and reset the network, which will allow you to econnect to the Internet, etc.

### Windows

(Info on how to create a loopback interface)

## Running the Labs

Start GNS3 by either running ```sudo ./gns3_run.sh``` in Linux or clicking the GNS3 icon in Windows.

>**NOTE** - In Linux, you must run the script. Do not run GNS3 from the Application menu or clicking the GNS3 icon.

When GNS3 starts, you will see a dialog asking you to create a new project. Enter "g001_ping" in the ***Name*** textbox and click the **OK** button.

![Project dialog](images/gns3_01.png)

In the main menu, click **Edit -> Preferences** or <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>. The **Preferences** window should appear. In the left-hand menu, click on **Server** and ensure that the value in the ***Host Binding*** textbox is "192.168.1.1":

![Preferences dialog](images/gns3_02.png)

Once again, look on the left-hand menu in the **Preferences** window, and select **Dynamips -> IOS Routers:**

![Preferences dialog](images/gns3_03.png)

When the **New IOS Router Template window** appears, ensure ***New Image*** is selected, and then click **Browse**:

![Preferences dialog](images/gns3_04.png)

When you installed GNS3, you also downloaded the IOS image for a Cisco 3745 Router. Select the image when the file window appears:

![Preferences dialog](images/gns3_05.png)

When asked, "Would like to decompress this IOS image?", click **Yes**:

![Preferences dialog](images/gns3_06.png)

Back in the **New IOS Router Template window**, click **Next >:**

![Preferences dialog](images/gns3_07.png)

When it comes to customizing the router's details, use the default values for both the name and memory and click on **Next >** for each:

![Preferences dialog](images/gns3_08.png)

![Preferences dialog](images/gns3_09.png)

The 3745 has 2 FastEthernet interfaces on its motherboard (GT96100-FE), 3 subslots for WICs (maximum of 6 serial ports) and 4 Network Module slots (maximum of 32 FastEthernet ports or 16 serial ports). For Network adapters, you have three options; we want all three for training. Place an option in each of the first open slots:

![Preferences dialog](images/gns3_10.png)

For WAN Interface Cards (WICs), we have two options. Once again, place an option in each of the first open slots:

![Preferences dialog](images/gns3_11.png)

Finally, accept the default Idle-PC value and click **Finish:** 

![Preferences dialog](images/gns3_12.png)

The IOS template's details appear. Note the memory for PCMCIA disk0; click on **Edit**, and set the PCMCIA disk0 to 1 MiB:

![Preferences dialog](images/gns3_13.png)

Click **OK**:

![Preferences dialog](images/gns3_14.png)

![Preferences dialog](images/gns3_15.png)
