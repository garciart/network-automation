# Adventures in Network Automation

## *Add*

- *WINDOWS_SETUP.md - Explain how to setup a loopback interface in Windows*
- *LINUX_SETUP.md - Explains how to setup a TAP interface in Linux*
- *CENTOS_INSTALL.md - Explain how to install GNS3 on Red Hat Enterprise Linux 7 (Maipo)/CentOS 7*

## Introduction

Recently, for personal and professional reasons (CompTIA, anyone?), I've delved into programming networking devices from within and without. Normally, in order to interact with a device, you must connect to them physically, via a serial or Ethernet cable, access their command-line interface (CLI), and enter commands manually or upload a script, usually written in Cisco's Tool Command Language (TCL).

This is fine if you have one switch or router, but if you have dozens or hundreds, this can become a full-time job. Wouldn't it be easier to write an application, let's say in Python, that can connect to a device; upload a configuration; reboot the device; and then test the device to ensure it is properly configured? The answer is you can write such a script, especially in Python, using modules such as subprocess and pexpect.

The bad news is that to test the program, you still need a physical device. You just can't download an Internetwork Operating System (IOS) image and interact with it using a hypervisor like VirtualBox. However, there are some great tools, like the Graphical Network Simulator-3 (GNS3), which can virtualize IOS images, and, with a little tweaking, can let you test your application.

This tutorial is broken down into three parts:

- Installing GNS3
- Connecting the host to the simulated device
- Labs to interact with the device

## Setup

### Linux

Setting up GNS3 in Ubuntu and Debian is pretty simple: check out [https://docs.gns3.com/docs/getting-started/installation/linux](https://docs.gns3.com/docs/getting-started/installation/linux "GNS3 Linux Install").

For our demo, however, we will use CentOS 7 (using 7.6, updated to 7.9) and Oracle VirtualBox Virtual Machine (VM) Manager. We did this, not because we're masochists, but because...

1. Many companies, especially government entities, use Red Hat Linux (i.e., the "commercial" version of CentOS), since it is a trusted OS which is [Protection Profile (PP) compliant](https://www.commoncriteriaportal.org/products/ "Certified Common Criteria Products").

2. While there were a lot of good posts and articles on how to do this, each of them were slightly different, so we distilled them into one set of instructions.

### Windows

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

## Running GNS3
