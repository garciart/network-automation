# Linux Instructions

## Introduction

Setting up GNS3 in Ubuntu and Debian is pretty simple: check out [https://docs.gns3.com/docs/getting-started/installation/linux](https://docs.gns3.com/docs/getting-started/installation/linux "GNS3 Linux Install").

For our demo, however, we will use CentOS and the following setup:

- Oracle VirtualBox Virtual Machine (VM) Manager(using 6.0.6)
- CentOS Linux 7 (using 3.10.0-957.e17.x86_84)
- GNOME Desktop Version 3.28.2

We did this, not because we're masochists, but because...

1. Many companies, especially government entities, use Red Hat Linux (i.e., the "commercial" version of CentOS), since it is a trusted OS which is [Protection Profile (PP) compliant](https://www.commoncriteriaportal.org/products/ "Certified Common Criteria Products").

2. While there were good posts and articles on how to do this, each of them were slightly different, so we distilled them into one set of instructions.

----------

## Setup

As we just said, we'll be using CentOS Linux 7 in VirtualBox for this demo, but you can use another virtual machine or an actual server if you like. Just make sure that your system has between 2-4GB of memory; at least 2 processor cores; 16GB of hard disk space; 32MB of video memory; and a connection to the Internet.

Since our focus is on getting GNS3 up and running, we won't get into creating a CentOS VM in VirtualBox. Several online walkthroughs exist: [Kurt Bando's tutorial](https://tutorials.kurtobando.com/install-a-centos-7-minimal-server-in-virtual-machine-with-screenshots/ "Install a CentOS 7 Minimal Server in Virtual Machine with screenshots") is an excellent example.

However, to make things easier, open "Software Selection" during installation and select "GNOME Desktop" instead of "Minimal Install" for your base environment. In addition, choose "Development Tools" and "System Administration Tools" as add-ons for the selected environment.

![Software Selection](images/centos02.png "Selecting Software")

You should also install Guest Additions to allow you to cut and paste between the host and the VM; an overview with instructions can be found [here](https://www.virtualbox.org/manual/ch04.html "Chapter 4. Guest Additions").

Once installation is complete, open a terminal and update the system using the following commands in the CLI:

    [gns3user@localhost ~]$ sudo yum -y update
    [gns3user@localhost ~]$ sudo yum -y install yum-utils
    [gns3user@localhost ~]$ sudo yum -y groupinstall development
    [gns3user@localhost ~]$ sudo yum groupinstall "GNOME Desktop"

This may take a while, especially on a new system.

Once the system update is completed, make sure that we have everything we need:

