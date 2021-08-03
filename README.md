# Adventures in Network Automation

***Disclaimer: The creators of GNS3 no longer recommend using Dynamips' Cisco IOS images, since the devices that use those images are no longer supported by Cisco. They recommend using more up-to-date images, such as QEMU or those available through Cisco's Virtual Internet Routing Lab (VIRL). However, since this tutorial is only a general introduction to network automation using Python, we will use the freely-available Dynamips images.***

***In addition, Cisco Packet Tracer, while an excellent tool, is not suitable for our purposes, since it cannot interact with the host or integrated development environments (IDEs) on those hosts.***

## Introduction

Recently, for personal and professional reasons, I've delved into programming networking devices from within and without. Normally, in order to interact with a device like a switch, you must connect to it physically, via a serial or Ethernet cable. Once connected, you would access the command-line interface (CLI), and enter commands manually or upload a script, usually written in Cisco's Tool Command Language (TCL).

This is fine if you have one switch or router, but if you have dozens or hundreds of devices, this can become a full-time job. Wouldn't it be easier to write an application, let's say in Python, that can connect to a device and enter the commands for you? The answer is yes; you can write such a script, especially with Python, using modules such as subprocess and pexpect.

The bad news is that, normally, to test the script, you will need a physical device. You just can't download an Internetwork Operating System (IOS) image, and then interact with it using a hypervisor like VirtualBox. However, there are some great tools, like the Graphical Network Simulator-3 (GNS3), which can virtualize IOS images. Also, with a little tweaking, they can let you test your code against a virtual network device.

This tutorial is broken down into three parts:

- [Installing GNS3 in CentOS](#installing-gns3-in-centos "Installing GNS3")
- [Setting up the environment](#setting-up-the-environment "Setting up the environment")
- [Running the Labs](#running-the-labs "Running the Labs")

>**NOTE** - Many thanks to David Bombal, Paul Browning, and many other incredible network gurus and coders (you know who you are :thumbsup: ).

-----

## Installing GNS3 in CentOS

Installing GNS on [Windows](https://docs.gns3.com/docs/getting-started/installation/windows/ "GNS3 Windows Install"), or Linux operating systems, such as [Ubuntu or Debian](https://docs.gns3.com/docs/getting-started/installation/linux "GNS3 Linux Install"), is pretty straight forward. However, we will be using CentOS 7.9 for labs and demos in this repository, and GNS3 doesn't work straight-out-of-the-box with Fedora, Red Hat Linux (RHEL), and CentOS.

>**NOTE** - Why are we using CentOS for this tutorial?
>- Approximately [20% of servers running Linux](https://w3techs.com/technologies/details/os-linux "Usage statistics of Linux for websites") use Fedora, RHEL, and CentOS. RHEL is also second, behind Microsoft, in [paid enterprise OS subscriptions](https://www.idc.com/getdoc.jsp?containerId=US46684720 "Worldwide Server Operating Environments Market Shares, 2019").
>- Many companies and government agencies, such as NASA and the DOD, use Red Hat Linux (i.e., the "commercial" version of CentOS), since it is a trusted OS which is [Protection Profile (PP) compliant](https://www.commoncriteriaportal.org/products/ "Certified Common Criteria Products").
>- I use Fedora, RHEL, or CentOS quite a bit, and I could not find a tutorial that captured all the steps involved in integrating GNS3 with the Fedora OS family.

To get started, download the latest ISO image of CentOS 7 from [the CentOS download page](https://www.centos.org/download/ "Download") and install it in a virtual machine. If you are not familiar with creating virtual machines, we recommend you review the instructions on the following sites:

- [Oracle VM VirtualBox User Manual](https://www.virtualbox.org/manual/ "Oracle VM VirtualBox User Manual")

- [VMware Workstation Player Documentation](https://docs.vmware.com/en/VMware-Workstation-Player/index.html "VMware Workstation Player Documentation")

- [Getting Started with Virtual Machine Manager](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/virtualization_getting_started_guide/chap-virtualization_manager-introduction "Getting Started with Virtual Machine Manager")

>**NOTE** - The focus of this tutorial is to use GNS3 to test our scripts, not to install operating systems or create virtual machines. There are many websites dedicated to setting up OS's and VM's, and we will not repeat those steps here.
> 
>However, whether you use VirtualBox or VMWare, make sure you:
> 
> 1. Allocate **2048 MB** of RAM to your machine  (e.g., in VirtualBox...):
> 
>    ![Memory size](images/a00.png "Settings -> Memory size")
>  
>2. Allocate at least **16 GB** of hard disk space to your machine (e.g., in VirtualBox...):
> 
>    ![File location and size](images/a01.png "Settings -> File location and size")**
> 
>3. Allocate **two** processors to your machine (e.g., in VirtualBox...):
> 
>    ![Settings -> System](images/a02.png "Settings -> System")
> 
>4. Add another network interface to your system. Make it private and isolate it from the outside world, by attaching it to an **Internal Network** in VirtualBox (shown) or connecting it to a **LAN segment** in VMWare:
> 
>    ![Network Settings](images/a03.png "Settings -> Network")
>
> In VMWare, you can make all the above changes to your VM, in the **Settings** window:
> 
>    ![Settings](images/a04.png)

Once you have finished creating your virtual machine, update and upgrade the OS.

>**NOTE** - If you are uing VirtualBox, we recommend installing Guest Additions, which will make interacting with your VM easier, by adding features like cut-and-paste from the host, etc. Check out [Aaron Kili's great article for TecMint on how to do that.](https://www.tecmint.com/install-virtualbox-guest-additions-in-centos-rhel-fedora/ "Install VirtualBox Guest Additions in CentOS, RHEL & Fedora") Just remember to execute the following commands before running the Guest Additions' ISO:
>
>```
>sudo yum -y install epel-release
>sudo yum -y update
>sudo yum install make gcc kernel-headers kernel-devel perl dkms bzip2
>sudo export KERN_DIR=/usr/src/kernels/$(uname -r)
>```
>
>Don't forget to reboot as well.

Open a Terminal and install git:

```sudo yum -y install git```

Next, clone this repository; it should appear in your home directory (e.g., ```/home/gns3user/Automation```):

```
[gns3user@localhost ~]$ git clone https://github.com/garciart/Automation.git
```

Now for the setup: There are a lot of good posts and articles on how to install GNS3 on CentOS. However, each of them are slightly different, so, to make life easier, we distilled them into [one executable shell script](gns3_setup_centos "CentOS Setup Script"). Before you run the script, we highly recommend you open it in an editor and look at its commands and comments, so you can become familiar with GNS3's dependencies.

Using elevated privileges, make the shell script executable and run it, piping the output into a text file. The install will take a few minutes, but once it is complete, check the text file for any errors.:

```
sudo chmod +x gns3_setup_centos
sudo ./gns3_setup_centos > setup_output.txt
grep -i -e "error" -e "warning" setup_output.txt
```

Examine and correct any errors; if necessary, delete the VM and start over again. Otherwise, if there are no errors, you can delete the output file and reboot the VM:

```
rm setup_output.txt
sudo reboot now
```

>**NOTE** - For the labs, you will need images for the Cisco 3745 Multiservice Access Router, with Advanced Enterprise Services, and the Cisco 7206VXR router. Both are older routers, but their Internetwork Operating Systems (IOS) are available for download, and they are sufficient for our labs.
>
>The [gns3_setup_centos](gns3_setup_centos "CentOS Setup Script") attempts to download the file from the [tfr.org](http://tfr.org "tfr.org") website, but if that fails, you can download the IOS' from other websites. Just remember to place them in the /GNS3/images/IOS folder in your home directory (e.g., ```/home/gns3user//GNS3/images/IOS```). Also, remember to check the md5 hash after downloading, to ensure you have not downloaded malware. Here are the names of the files, their hashes, and some additional information:
>
>- Cisco 3745 Multiservice Access Router:
>   * IOS version 12.4.25d (Mainline):
>   * File Name: c3745-adventerprisek9-mz.124-25d.bin
>   * MD5: 563797308a3036337c3dee9b4ab54649
>   * Flash Memory: 64MB
>   * DRAM: 256MB
>   * End-of-Sale Date: 2007-03-27
>   * End-of-Support Date: 2012-03-27
>   * IOS End-of-Support Date: 2016-01-31
>- Cisco 7206VXR router:
>   * IOS version 12.4.25g (Mainline):
>   * File Name: c7200-a3jk9s-mz.124-25g.bin
>   * Flash Memory: 64MB
>   * DRAM: 256MB
>   * MD5: 3a78cb61831b3ef1530f7402f5986556
>   * End-of-Sale Date: 2012-09-29 
>   * End-of-Support Date: 2017-09-30
>   * IOS End-of-Support Date: 2016-01-31

-----

## Setting up the environment

Before we start, here's the subnet info for the network:

```
- Network Address: 192.168.1.0/24
- Subnet Mask: 255.255.255.0 (ff:ff:ff:00)
- GNS3 Host Device IP Address: 192.168.1.1/32
- Gateway IP Address: 192.168.1.1/32
- Total Number of Hosts: 256
- Number of Usable Hosts: 254
- Usable IP Range: 192.168.1.2 - 192.168.1.254
- Broadcast Address: 192.168.1.255
- IP Class and Type: C (Private)
```

In CentOS, network interfaces for Ethernet will start with ```em```, ```en```, and ```et``` (e.g., ```em1```, ```eth0```, etc.). Open a Terminal and look for your isolated network interface, by inputting ```ip addr show label e*```:

```
[gns3user@localhost ~]$ ip addr show label e*
2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether 08:00:27:cf:12:5e brd ff:ff:ff:ff:ff:ff
    inet 10.0.2.15/24 brd 10.0.2.255 scope global noprefixroute dynamic enp0s3
       valid_lft 81729sec preferred_lft 81729sec
    inet6 fe80::91fc:27c4:403f:848f/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
3: enp0s8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether 08:00:27:87:ff:e2 brd ff:ff:ff:ff:ff:ff
[gns3user@localhost ~]$ 
```

Look for the interface that does not have an IP address. In this case, the isolated interface is named ```enp0s8```. Give the interface an IPv4 address, by inputting ```sudo ip addr add 192.168.1.1/24 dev enp0s8```. Do not forget to add the subnet (```/24```), or the ```ip``` program, by default, will set a netmask of 255.255.255.255 (```/32```), which will allow only one host on the isolated network, instead of a netmask of 255.255.255.0, which will allow the 256 hosts we want:

```
[gns3user@localhost ~]$ sudo ip addr add 192.168.1.1/24 dev enp0s8
[sudo] password for gns3user: 
[gns3user@localhost ~]$ ip addr show enp0s8
3: enp0s8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether 08:00:27:87:ff:e2 brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.1/24 scope global enp0s8
       valid_lft forever preferred_lft forever
[gns3user@localhost ~]$ 
```

Open a Terminal and start GNS3:

```
gns3
```

A Setup wizard will appear. Select **Run appliances on my local computer** and click **Next>**:

![Setup Wizard](images/a05.png)

In **Local sever configuration**, under **Host binding**, select the isolated interface:

![Local sever configuration](images/a06.png)

After a few minutes, a **Local server status** window will appear, letting you know that a "Connection to the local GNS3 server has been successful!". Click **Next>** to continue:

![Local server status](images/a07.png)

At the **Summary** window, click **Finish**:

![Setup Wizard Summary](images/a08.png)

>**NOTE** - If you run into any errors, exit GNS3 and check your IP addresses. Restart GNS3 and select **Edit** -> **Preferences**, or press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>. Select **Server** and set the **Host binding** to the the isolated interface's IP address: 
>
>![Preferences](images/a09.png)
>

## Running the Labs

Click on **File** ->  **New blank project**, or press  <kbd>Ctrl</kbd>+<kbd>N</kbd>, to create a new project. If GNS3 is not running, start GNS3 by inputting ```gns3``` in a Terminal (the **Project** window should appear).

You will see a dialog asking you to create a new project. Enter "g001_ping" in the ***Name*** textbox and click the **OK** button.

![Project dialog](images/a10.png)

When the main window reappears, click **Edit -> Preferences** or <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>. The **Preferences** window should appear. In the left-hand menu, click on **Server** and ensure that the value in the ***Host Binding*** textbox is "192.168.1.1":

![Preferences dialog](images/a11.png)

Once again, look in the left-hand menu in the **Preferences** window, and select **Dynamips -> IOS Routers** and click on **New:**

![Preferences dialog](images/a12.png)

When the **New IOS Router Template window** appears, ensure ***New Image*** is selected, and then click **Browse**:

![Preferences dialog](images/a13.png)

When you installed GNS3, you also downloaded the IOS image for a Cisco 3745 Router. Select the image when the file window appears and click **Open** at the top:

![Preferences dialog](images/a14.png)

When asked, "Would like to decompress this IOS image?", click **Yes**:

![Preferences dialog](images/a15.png)

Back in the **New IOS Router Template window**, click **Next >:**

![Preferences dialog](images/a16.png)

When it comes to customizing the router's details, use the default values for both the name and memory and click on **Next >** for each:

![Preferences dialog](images/a17.png)

![Preferences dialog](images/a18.png)

Here is the back of a 3745 Router:

![Cisco 3745 back](images/a19.png)

 In between the power supply modules, from top to bottom, the 3745 has:
 
 - Three (3) WAN interface card (WIC) slots
 - A console (light blue) and an auxilary port (black) on the right, a CompactFlash (CF) memory card slot in the center, and two (2) built-in FastEthernet interfaces (GT96100-FE), which correspond to FastEthernet 0/0 and 0/1. By the way, when you interact with the router directly in GNS3, you are using a simulated connection to the console port. However, our Python scripts will connect to the router through the Ethernet cable, using either Telnet or SSH.
- Four (4) network adapter module slots.

For network adapter modules, you have three options; we want all three for training. Place one option each in an open slot:

- NM-1FE-TX 1-Port 10/100 Mbps Fast Ethernet Network Module
- NM-4T 4 port Synchronous Serial Network Module
- NM-16ESW 16-Port 10/100 Mbps Fast Ethernet Switch (EtherSwitch) Module

![Preferences dialog](images/a20.png)

For WAN Interface Cards (WICs), we have two options. Once again, place an option in each of the first open slots:

- WIC-1T One port serial (DB60, Cisco 60-pin "5-in-1" connector )
- WIC-2T Two port serial (DB60, Cisco 60-pin "5-in-1" connector )

>**NOTE** - For more information on these modules and other configurations, check out the [Cisco 3700 Series Router Hardware](https://www.cisco.com/web/ANZ/cpp/refguide/hview/router/3700.html "
CISCO 3700 Series Router Hardware View") page. If the site becomes unavailable, we have also included [a pdf copy here.](/3700.pdf "CISCO 3700 Series Router Hardware View")

![Preferences dialog](images/a21.png)

Finally, accept the default Idle-PC value and click **Finish:** 

![Preferences dialog](images/a22.png)

The IOS template's details appear. Note the memory for the Personal Computer Memory Card International Association (PCMCIA) disk0. This is the device's CompactFlash (CF) memory card, used to store the system image, configuration files, and more. It cannot be 0, and the cards hold 32, 64, and 128 MiB of memory. Click on **Edit** to change it:

![Preferences dialog](images/a23.png)

Select the **Memories and disks** tab. Set the PCMCIA disk0 to 64 MiB and click **OK**:

![Preferences dialog](images/a24.png)

This brings you back to the template details page. There is some good information here, such as the name of the startup configuration file:

![Preferences dialog](images/a25.png)

 Once you are done, click **OK** to return to the main window.

Now that you have finished setting up your lab environment, 

![Preferences dialog](images/gns3_16.png)

![Preferences dialog](images/gns3_17.png)

![Preferences dialog](images/gns3_18.png)

![Preferences dialog](images/gns3_19.png)

![Preferences dialog](images/gns3_20.png)

![Preferences dialog](images/gns3_21.png)

One way to detect hosts on your subnet is to run ```nmap -sP 192.168.1.1-255```:

![Preferences dialog](images/gns3_21a.png)

![Preferences dialog](images/gns3_22.png)

![Preferences dialog](images/gns3_23.png)

>**NOTE** - We will use nmap and other CLI tools in this tutorial. Therefore, open a terminal and ensure you have installed the following packages:
> ```
> - sudo yum -y install net-tools
> - sudo yum -y install nmap
> - sudo yum -y install lsof
> ```
