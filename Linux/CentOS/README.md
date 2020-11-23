# Linux Instructions

## Introduction

Setting up GNS3 in Ubuntu and Debian is pretty simple: check out [https://docs.gns3.com/docs/getting-started/installation/linux](https://docs.gns3.com/docs/getting-started/installation/linux "GNS3 Linux Install").

For our demo, however, we will use CentOS 7 (using 7.6, updated to 7.9) and Oracle VirtualBox Virtual Machine (VM) Manager. We did this, not because we're masochists, but because...

1. Many companies, especially government entities, use Red Hat Linux (i.e., the "commercial" version of CentOS), since it is a trusted OS which is [Protection Profile (PP) compliant](https://www.commoncriteriaportal.org/products/ "Certified Common Criteria Products").

2. While there were a lot of good posts and articles on how to do this, each of them were slightly different, so we distilled them into one set of instructions.

----------

## Setup

As we just said, we'll be using CentOS Linux 7 in VirtualBox for this demo, but you can use another virtual machine or an actual server if you like. Just make sure that your system has between 2-4GB of memory; at least 2 processor cores; 16GB of hard disk space; 32MB of video memory; and a connection to the Internet.

----------

![Setting RAM size during VB setup...](images/centos01.png "Setting RAM size during VB setup...")
![Setting RAM size after VB setup...](images/centos01a.png "Setting RAM size after VB setup...")

----------

![Setting disk size size during VB setup...](images/centos02.png "Setting disk size size during VB setup...")

----------

![Setting the number of cores after VB setup...](images/centos03.png "Setting the number of cores after VB setup...")

----------

![Setting video memory size after VB setup...](images/centos04.png "Setting video memory size after VB setup...")

----------

![Adding the install disk to secondary storage...](images/centos05.png "Adding the install disk to secondary storage...")

----------

Since our focus is on getting GNS3 up and running, we won't get into creating a CentOS VM in VirtualBox. Several online walkthroughs exist: [Kurt Bando's tutorial](https://tutorials.kurtobando.com/install-a-centos-7-minimal-server-in-virtual-machine-with-screenshots/ "Install a CentOS 7 Minimal Server in Virtual Machine with screenshots") is an excellent example.

However, to make things easier, when he tells you to click "Begin Installation" on the the "Installation Summary" screen, click on "Software Selection" (under the "Software" heading) instead. Change your base environment to "GNOME Desktop" instead of "Minimal Install". In addition, choose "Development Tools" as an add-on for the selected environment.

![Software Selection](images/centos06.png "Selecting Software")

![Software Selection](images/centos07.png "Selecting Software")

You may also want to set up an internet connection in order to download the repo, wget necessary files, etc.

![Add an internet connection](images/centos08.png "Add an internet connection")

You should also install Guest Additions to allow you to cut and paste between the host and the VM; an overview with instructions can be found [here](https://www.virtualbox.org/manual/ch04.html "Chapter 4. Guest Additions").

![VirtualBox Guest Additions](images/centos09.png "VirtualBox Guest Additions")

Once installation is complete, open a terminal and update the system using the following commands in the CLI:

    [gns3user@localhost ~]$ sudo yum -y install yum-utils
    [gns3user@localhost ~]$ sudo yum -y update

![Update CentOS](images/centos10.png "Update CentOS")

This may take a while, especially on a new system.

Once the system update is completed, make sure that we have everything we need:

