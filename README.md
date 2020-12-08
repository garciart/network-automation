# Adventures in Network Automation

## *Add*

- *WINDOWS_SETUP.md - Explain how to setup a loopback interface in Windows*
- *LINUX_SETUP.md - Explains how to setup a TAP interface in Linux*
- *CENTOS_INSTALL.md - Explain how to install GNS3 on Red Hat Enterprise Linux 7 (Maipo)/CentOS 7*

## Introduction

Recently, for personal and professional reasons (CompTIA, anyone?), I've delved into programming networking devices from within and without. Normally, in order to interact with a device like a switch, you must connect to it physically, via a serial or Ethernet cable, access its command-line interface (CLI), and enter commands manually or upload a script, usually written in Cisco's Tool Command Language (TCL).

This is fine if you have one switch or router, but if you have dozens or hundreds of devices, this can become a full-time job. Wouldn't it be easier to write an application, let's say in Python, that can connect to a device; upload a configuration; reboot the device; and then test the device to ensure it is properly configured? The answer is yes; you can write such a script, especially with Python, using modules such as subprocess and pexpect.

The bad news is that to test the program, you will still need a physical device. You just can't download an Internetwork Operating System (IOS) image, and then interact with it using a hypervisor like VirtualBox. However, there are some great tools, like the Graphical Network Simulator-3 (GNS3), which can virtualize IOS images, and, with a little tweaking, can let you test your code against a network device.

This tutorial is broken down into three parts:

- Installing GNS3
- Setting up the environment
- Overview of the Labs

Many thanks to David Bombal, Paul Browning, and many other incredible coders and network gurus (you know who you are :thumbsup:).

-----

## Installing GNS3

### Linux

Setting up GNS3 in Ubuntu and Debian is pretty simple: check out [https://docs.gns3.com/docs/getting-started/installation/linux](https://docs.gns3.com/docs/getting-started/installation/linux "GNS3 Linux Install").

However, GNS3 doesn't work straight-out-of-the-box with Fedora, Red Hat Linux (RHEL), and CentOS. But before kicking them to the curb, remember...

1. Approximately [20% of servers running Linux](https://w3techs.com/technologies/details/os-linux "Usage statistics of Linux for websites") use one of these operating systems, and RHEL is second, behind Microsoft, in [paid enterprise OS subscriptions](https://www.idc.com/getdoc.jsp?containerId=US46684720 "Worldwide Server Operating Environments Market Shares, 2019").

2. Many companies and government agencies, such as NASA and the DOD, use Red Hat Linux (i.e., the "commercial" version of CentOS), since it is a trusted OS which is [Protection Profile (PP) compliant](https://www.commoncriteriaportal.org/products/ "Certified Common Criteria Products").

We used Centos 7 for the labs and demos in this repository. While there were a lot of good posts and articles on how to install GNS3 on CentOS, each of them were slightly different, so we distilled them into [one shell script](gns3_setup_centos.sh "CentOS Setup Script").

### Windows

Installing GNS3 on windows is also relatively simple; check out [https://docs.gns3.com/docs/getting-started/installation/windows/](https://docs.gns3.com/docs/getting-started/installation/windows/ "GNS3 Windows Install"). David Bombal also has a [great video sereis on using GNS3](https://www.youtube.com/watch?v=Ibe3hgP8gCA&list=PLhfrWIlLOoKNFP_e5xcx5e2GDJIgk3ep6&index=1&ab_channel=DavidBombal "GNS3 Installation - David Bombal"), starting with installation; highly recommended!

-----

## Setting up the environment
