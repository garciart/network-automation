# Linux Instructions

## Introduction

Setting up GNS3 in Ubuntu and Debian is pretty simple: check out [https://docs.gns3.com/docs/getting-started/installation/linux](https://docs.gns3.com/docs/getting-started/installation/linux "GNS3 Linux Install")

For our demo, however, we will use CentOS and the following setup:

- Oracle VirtualBox Virtual Machine (VM) Manager(using 6.0.6)
- CentOS Linux 7 (using 3.10.0-957.e17.x86_84)
- GNOME Desktop Version 3.28.2
- Python 3 Programming Language Interpreter (using version 3.6.8)

We did this, not because we're masochists, but because...

1. Many companies, especially government entities, use Red Hat Linux, since it is a trusted OS which is [Protection Profile (PP) compliant](https://www.commoncriteriaportal.org/products/ "Certified Common Criteria Products").

2. While there were good posts and articles on how to do this, each of them were slightly different, so we distilled them into one set of instructions.

----------

## Setup

As we just said, we'll be using CentOS Linux 7 in VirtualBox for this demo, but you can use another virtual machine or an actual server if you like. Just make sure that your system has at least 2GB of memory; 16GB of hard disk space; 32MB of video memory; and a connection to the Internet.

We'll start with the default minimal install option. Since our focus is on getting GNS3 up and running, we won't get into creating a CentOS VM in VirtualBox. Several online walkthroughs exist:  [Kurt Bando's tutorial](https://tutorials.kurtobando.com/install-a-centos-7-minimal-server-in-virtual-machine-with-screenshots/ "Install a CentOS 7 Minimal Server in Virtual Machine with screenshots")  is an excellent example.

Once your VM is setup, and to start things off right, let's create a super user to avoid using the root user:

    [root@localhost ~]# adduser gns3user
    [root@localhost ~]# passwd gns3user
    Changing password for user gns3user.
    New password: ************
    Retype new password: ************
    passwd: all authentication tokens updated successfully.
    [root@localhost ~]# gpasswd -a gns3user wheel
    Adding user gns3user to group wheel
    [root@localhost ~]# su - gns3user
    [gns3user@localhost ~]$

If you want to connect to the Internet using an existing WiFi access point, instead of an ethernet cable, use the Network Manager Text User Interface (nmtuui):

    [gns3user@localhost ~]$ chkconfig NetworkManager on
    Note: Forwarding request to 'systemctl enable NetworkManager.service'.
    ==== AUTHENTICATING FOR org.freedesktop.systemd1.manage-unit-files ===
    Authentication is required to manage system services or unit files.
    Authenticating as: gns3user
    Password: ************ 
    ==== AUTHENTICATION COMPLETE ===
    ==== AUTHENTICATING FOR org.freedesktop.systemd1.reload-daemon ===
    Authentication is required to reload the systemd state.
    Authenticating as: gns3user
    Password: ************
    ==== AUTHENTICATION COMPLETE ===
    [gns3user@localhost ~]$ service NetworkManager start
    ==== AUTHENTICATING FOR org.freedesktop.systemd1.manage-units ===
    Authentication is required to manage system services or units.
    Authenticating as: gns3user
    Password: ************
    ==== AUTHENTICATION COMPLETE ===
    [gns3user@localhost ~]$ nmtui

The TUI should appear. Select "Activate a Connection" and find your AP. Enter your password; you should then be connected.

![Using nmtui](images/centos01.png)

----------

![Using nmtui](images/centos02.png)

Next, update the system and add CentOS' development tools using the following commands in the CLI:

    [gns3user@localhost ~]$ sudo yum -y update
    [gns3user@localhost ~]$ sudo yum -y install yum-utils
    [gns3user@localhost ~]$ sudo yum -y groupinstall development

This may take a while, especially on a new system.

Once the system update is completed, make sure that we have everything we need:
