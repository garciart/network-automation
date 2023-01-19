# Ansible and Ansible Automation Platform Setup

This tutorial will walk you through installing Ansible and Ansible Automation Platform on a virtual control node.

- [Prerequisites](#prerequisites)
- [Create the Virtual Machine](#create-the-virtual-machine)
- [Prepare the Control Node](#prepare-the-control-node)
- [Register the Control Node](#register-the-control-node)
- [Update the Control Node](#update-the-control-node)
- [Install Ansible](#install-ansible)
- [Create Your First Playbook](#create-your-first-playbook)
- [Create a Remote Node](#create-a-remote-node)
- [Run Playbooks against the Remote Node](#run-playbooks-against-the-remote-node)
- [Install the Ansible Automation Platform](#install-the-ansible-automation-platform)
- [Notes](#notes)

----

## Prerequisites

- System requirements:
  - A processor capable of running eight (8) CPU threads.
  - At least 16 GB of RAM.
  - At least 160 GB hard drive.
- An active [Red Hat Developer account](http://access.redhat.management "Red Hat Developer account").
- An optical disc image (ISO) of Red Hat Enterprise Linux operating system, version 8.4 or later, for x86_64 computers (I used RHEL 8.6 for this tutorial, available, with subscription, at https://access.redhat.com/downloads).
- A subscription to the Ansible Automation Platform (AAP) (you can use the *60 Day Product Trial of Red Hat Ansible Automation Platform* for this tutorial).
- A Type-2 hypervisor, such as VirtualBox or VMWare.

For more information on AAP requirements, see https://access.redhat.com/documentation/en-us/red_hat_ansible_automation_platform/2.2/html/red_hat_ansible_automation_platform_installation_guide/index.

----

## Create the Virtual Machine

1. Create a virtual machine, named *"ansible_control"*, per the hypervisor's instructions:

   - [Oracle VM VirtualBox User Manual](https://www.virtualbox.org/manual/ "Oracle VM VirtualBox User Manual")
   - [VMware Workstation Player Documentation](https://docs.vmware.com/en/VMware-Workstation-Player/index.html "VMware Workstation Player Documentation")
   - [Getting Started with Virtual Machine Manager](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/virtualization_getting_started_guide/chap-virtualization_manager-introduction "Getting Started with Virtual Machine Manager")

   Ensure the virtual machine has:

   - At least two (2) CPUs.
   - At least 8192 MB RAM for installation of AAP, and 4096 MB RAM for operation.
   - At least 40 GB of hard drive space. If you are separating your drive into multiple partitions, you must allocate at least 20 GB to `/var`.

   > **NOTE** - Since the focus of this tutorial is using Ansible, and for the sake of brevity, I will avoid going into great detail on how to create virtual machines or install operating systems. In addition, the links provided in this section are maintained y their respective companies, and contain the latest instructions for creating a VM or installing RHEL 8.

3. However, before you start the VM, go to its network settings, and change the network connection to **Bridged Adapter**. This will allow the VM to access the host, the Internet, and other VM's.

4. Start the VM. When prompted for the location of the installation media, navigate to the location of the RHEL 8 ISO, and select the ISO.

5. Install RHEL 8, per the instructions at https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/performing_a_standard_rhel_8_installation/installing-rhel-on-adm64-intel-64-and-64-bit-arm.

----

## Prepare the Control Node

1. Log into the control node and open a Terminal.

2. Check if a **control** user account exists:

    ```
    id control
    ```

- If the **control** user account exists, make it an administrator:
    
    ```
    sudo usermod -aG wheel control
    ```
    
- If the **control** user account does not exist, create the account and switch to it:
    
    ```
    # sudo useradd  --comment "Ansible Control Node Account" --create-home -groups wheel control
    sudo useradd -c "Ansible Control Node Account" -m -G wheel control
    echo <desired password> | sudo passwd control --stdin
    ```

3. Switch to the **control** user account:

    ```
    exec su - control
    ```

4. Even though you have created a user with a password, it is better to use Secure Shell (SSH) keys for authentication credentials. Generate a private/public key pair for the control node:

    ```
    ssh-keygen
    ```

5. When prompted where to save the key, press **[Enter]** to accept the default value.

6. When prompted to enter a passphrase, press **[Enter]** twice to skip entering a passphrase.

    > **NOTE** - If you use a passphrase, you will have to enter the passphrase when connecting to remote nodes. However, you can also start the `ssh-agent` daemon and use `ssh-add` to automatically add the passphrase when negotiating with the remote node. More information is available [here](https://linux.die.net/man/1/ssh-add).

7. The system will save your private key in the hidden `~/.ssh/id_rsa` file, and the public key in the hidden `~/.ssh/id_rsa.pub` file. Remember the public key's location; you will use it later in a playbook.

8. Get the IPv4 address and netmask of the Ethernet interface you will use to configure remote nodes with Ansible:

    ```
    # ifconfig | grep --extended-regexp "^e[mnt]" --after-context=2
    ifconfig | grep -E "^e[mnt]" -A 2
    ```

    > **NOTE** - The IPv4 address and its netmask will appear after the Internet Protocol version 4 family identifier, **inet**. For example:
    >
    > ```
    > inet 192.168.0.x  netmask 255.255.255.0  broadcast 192.168.0.x
    > ```

9. If no IPv4 address appears, set an IPv4 address using the following command:

    ```
    sudo ifconfig <open Ethernet interface> <desired IPv4 address> netmask <desired subnet mask>
    ```

10. Open your `hosts` file for editing:

    ```
    sudo vim /etc/hosts
    ```

11. Replace the localhost domain with a unique, but intuitive domain name (e.g., `control.example.com`, etc.) for both the localhost IPv4 address (`127.0.0.1`) and IPv6 address (`::1`). In addition, add information for your Ethernet IPv4 address:

    > **NOTE** - In this tutorial, you will only create one control node. However, if you needed more than one control node, you can create and use a naming convention for control nodes, such as `control_1`, etc.

    ```
    127.0.0.1             localhost   control.example.com
    ::1                   localhost   control.example.com
    <your IPv4 address>   control     control.example.com
    ```

12. Save the file by pressing [Esc], then [:]. Enter "wq" at the **":"** prompt.

13. Open your `hostname` file for editing:

    ```
    sudo vim /etc/hostname
    ```

14. Replace the hostname of the control node with the new domain name:

    ```
    control.example.com
    ```

15. Save the file by pressing [Esc], then [:]. Enter "wq" at the **":"** prompt.

16. Reboot the control node to incorporate the changes:

    ```
    sudo reboot now
    ```

17. Once the control node has finished rebooting, log in using the **control** user account.

    > **NOTE** - Clear out any "Welcome" dialog windows that may appear.

----

## Register the Control Node

To update the control node, as well as to use Ansible Tower or the Ansible Automation Platform, you must have a RedHat subscription.

1. Open a Terminal.

2. Register the control node. Enter your Red Hat password when prompted:

    ```
    sudo subscription-manager register --username <RedHat subscription username>
    ```

3. Once you have registered the control node, pull the subscription data from the server, and set the control node to automatically attach any compatible or related subscriptions:

    ```
    sudo subscription-manager refresh
    sudo subscription-manager auto-attach --enable
    ```

    > **NOTE** - You can check if the control node was registered at https://access.redhat.com/management/systems.

----

## Update the Control Node

4. Update the control node (this may take a while):

    ```
    sudo yum -y update
    sudo yum -y upgrade
    sudo yum -y clean all
    sudo yum -y autoremove
    ```

    > **NOTE** - If you are using VirtualBox, I recommend installing their Guest Additions software suite, which will make interacting with your VM easier, by adding features like cut-and-paste, shared folders, etc. Check out Aaron Kili's great article, ["Install VirtualBox Guest Additions in CentOS, RHEL & Fedora."](https://www.tecmint.com/install-virtualbox-guest-additions-in-centos-rhel-fedora/ "Install VirtualBox Guest Additions in CentOS, RHEL & Fedora.") Just remember to execute the following commands in a Terminal before running the software on the Guest Additions' ISO:
    >
    > ```
    > sudo subscription-manager repos --enable codeready-builder-for-rhel-8-$(arch)-rpms
    > sudo dnf -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
    > sudo yum -y install make gcc kernel-headers kernel-devel perl dkms bzip2 git
    > sudo reboot now
    > ```
    >
    > By the way, if you need to enable Guest Additions on another operating system, replace the first two lines with the appropriate lines from https://docs.fedoraproject.org/en-US/epel/.
    >
    > Once the control node has finished rebooting, log in using the **control** user account. Open a Terminal and run the **Files** application:
    >
    > ```
    > nautilus
    > ```
    >
    > Select the Guest Additions' ISO and run the software. You can also run the software from the command line (in my case, the command was `sudo ./run/media/control/VBox_GAs_6.1.38/autorun.sh`).
    >
    > Do not forget to reboot the control node again after installing the software.

----

## Install Ansible

1. Open a Terminal.

2. Before installing Ansible, ensure that Python 3.9 or higher is installed on the control node:

    ```
    python3 -V
    ```

3. If the version is less than 3.9, upgrade Python:

    ```
    sudo yum -y install python3.9
    sudo alternatives --set python3 /usr/bin/python3.9
    ```

4. Install Ansible:

    ```
    sudo yum -y install ansible
    ansible --version
    ```

5. Test Ansible by pinging the localhost using Ansible's **ping** module:

    > **NOTE** - Ansible's built-in **ping** module is not the same as Linux ping; it does not send out Internet Control Message Protocol (ICMP) packets. Instead, the module checks that it can connect to a node, using SSH, and determine the Python version installed on the node.

    ```
    ansible -m ping localhost
    ```

- **Output:**

    ```
    localhost | SUCCESS => {
        "changed": false,
        "ping": "pong"
    }
    ```

    > **NOTE** - If you intend to do a lot of command-line work, you can also install the optional auto-complete package, which allows you to use the **[Tab]** key to complete Ansible arguments:
    >
    > ```
    > sudo python3 -m pip install --user argcomplete
    > ```

6. [To avoid exposing your inventories, playbooks, etc., to anyone with administrator privileges](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#avoiding-security-risks-with-ansible-cfg-in-the-current-directory), do not use the default `/etc/asible` directory. Instead, create an Ansible sub-directory in your Home directory, then navigate to it (if prompted, enter your password):

    ```
    # sudo mkdir --parents ~/Ansible
    sudo mkdir -p ~/Ansible
    cd ~/Ansible
    ```

7. Create an Ansible inventory file:

    ```
    sudo vim ~/Ansible/inventory.yml
    ```

    > **NOTE** - To make life easy, use *inventory.yml* for your inventory of nodes, instead of *hosts*, to avoid naming conflicts with other files named *hosts*.

8. Press [i], and enter the following YAML code:

    ```
    ---
    
    control_nodes:
      hosts:
        control:
          ansible_host: <your IPv4 address>
          ansible_connection: ssh
          ansible_ssh_user: control
          ansible_ssh_pass: <the control node password>
    ```

9. Save the file by pressing [Esc], then [:]. Enter "wq" at the **":"** prompt.

10. Create an Ansible configuration file:

    ```
    sudo vim ~/Ansible/ansible.cfg
    ```

11. Press [i], and enter the following YAML code:

    ```
    [defaults]
    # Stop host key checking, as well as populating the known_hosts file, for now
    # https://docs.ansible.com/ansible/2.5/user_guide/intro_getting_started.html#host-key-checking
    host_key_checking = False
    # https://docs.ansible.com/ansible/latest/reference_appendices/config.html#avoiding-security-risks-with-ansible-cfg-in-the-current-directory
    inventory = ~/Ansible/inventory.yml
    ```

12. Save the file by pressing [Esc], then [:]. Enter "wq" at the **":"** prompt.

13. Test Ansible by listing your nodes:

    ```
    # ansible all --list-hosts --inventory ~/Ansible/inventory.yml
    ansible all --list-hosts -i ~/Ansible/inventory.yml
    ```

14. Test Ansible by running Ansible's **ping** module:

    ```
    # ansible all --module-name ping --inventory ~/Ansible/inventory.yml
    ansible all -m ping -i ~/Ansible/inventory.yml
    ```

15. Test Ansible by running an ad-hoc command:

    ```
    ansible all -a "ping -c 4 8.8.8.8"
    ```

----

## Create Your First Playbook

For your first playbook, you will say "Hello, World!", using the ansible.builtin.debug module

1. Create the playbook:

    ```
    sudo vim ~/Ansible/first_playbook.yml
    ```

2. Press [i], and enter the following YAML code:

    ```
    ---
    
    - name: First playbook
      hosts: control
      tasks:
      - name: Say Hello using the ansible.builtin.debug module
        debug:
          msg: Hello, World!
    ```

3. Save the file by pressing [Esc], then [:]. Enter "wq" at the **":"** prompt.

4. Run the playbook:

    ```
    ansible-playbook ~/Ansible/first_playbook.yml
    ```

- **Output:**

    ```
    PLAY [First playbook] *********************************************************************************************************************************************************************************************
    
    TASK [Gathering Facts] ********************************************************************************************************************************************************************************************
    ok: [control]
    
    TASK [Say Hello using the ansible.builtin.debug module] ***********************************************************************************************************************************************************
    ok: [control] => {
        "msg": "Hello, World!"
    }
    
    PLAY RECAP ********************************************************************************************************************************************************************************************************
    control                    : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
    ```

5. Ansible performed a task that you did not explicitly ask it to do: it gathered *facts* about the node. Create another playbook to display these facts:

    ```
    sudo vim ~/Ansible/second_playbook.yml
    ```

6. Press [i], and enter the following YAML code:

    ```
    ---
    
    - name: Second playbook
      hosts: control
      tasks:
      - name: Print the facts, nothing but the facts
        debug:
          var: ansible_facts
    ```

7. Save the file by pressing [Esc], then [:]. Enter "wq" at the **":"** prompt.

8. Run the playbook:

    ```
    ansible-playbook ~/Ansible/second_playbook.yml
    ```

9. That is a lot of facts! However, you can reference any of these facts, as well as restricted Ansible variables, in your playbooks. Create another playbook to display these facts and variables:

    ```
    sudo vim ~/Ansible/third_playbook.yml
    ```

10. Press [i], and enter the following YAML code:

    ```
    ---
    
    - name: Third playbook
      hosts: control
      tasks:
      - name: Print a fact, without titles
        debug:
          var: ansible_facts.env.SSH_CLIENT
    
      - name: Print a magic variable, without titles
        debug:
          var: ansible_host
    
      - name: Print only certain facts and variables, with and without titles
        debug:
          msg:
          - Hostname - {{ ansible_facts.hostname }}
          - "{{ ansible_facts.env.SSH_CLIENT }}"
    
      - name: Print environment variables
        debug:
          msg:
          - Home directory - {{ lookup('env', 'HOME') }}
          - "{{ hostvars['control'].ansible_default_ipv4.address }}"
    ```

11. Save the file by pressing [Esc], then [:]. Enter "wq" at the **":"** prompt.

12. Run the playbook:

    ```
    ansible-playbook ~/Ansible/third_playbook.yml
    ```

    - **Output:**

    ```
    PLAY [Third playbook] *********************************************************************************************************************************************************************************************
    
    TASK [Gathering Facts] ********************************************************************************************************************************************************************************************
    ok: [control]
    
    TASK [Print a fact, without titles] *******************************************************************************************************************************************************************************
    ok: [control] => {
        "ansible_facts.env.SSH_CLIENT": "192.168.0.29 42554 22"
    }
    
    TASK [Print a magic variable, without titles] *********************************************************************************************************************************************************************
    ok: [control] => {
        "ansible_host": "control"
    }
    
    TASK [Print only certain facts and variables, with and without titles] ********************************************************************************************************************************************
    ok: [control] => {
        "msg": [
            "Hostname - control",
            "192.168.0.29 42554 22"
        ]
    }
    
    TASK [Print an environment variable] ******************************************************************************************************************************************************************************
    ok: [control] => {
        "msg": [
            "Home directory - /home/control",
            "192.168.0.29"
        ]
    }
    
    PLAY RECAP ********************************************************************************************************************************************************************************************************
    control                    : ok=5    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
    ```

13. Now, create a playbook that uses modules and perform the following tasks:

    - Ping the control node using the ansible.builtin.ping module, and save the result
    - Print the result of the ansible.builtin.ping module, using the ansible.builtin.debug module
    - Ping the control node using the ansible.builtin.command module and the Linux ping command, and save the result
    - Print the result of the ansible.builtin.command module, using the ansible.builtin.debug module
    - Print the results of the last two commands

    ```
    sudo vim ~/Ansible/fourth_playbook.yml
    ```

14. Press [i], and enter the following YAML code:

    ```
    ---
    
    - name: Fourth playbook
      hosts: control
      tasks:
      - name: Ping the control node using the ansible.builtin.ping module, and save the result
        ping:
        register: ansible_ping_result
    
      - name: Print the result of the ansible.builtin.ping module, using the ansible.builtin.debug module
        debug:
          var: ansible_ping_result
    
      - name: Ping the control node using the ansible.builtin.command module and the Linux ping command, and save the result
        command: 'ping -c 4 "{{ ansible_host }}"'
        register: icmp_ping_result
    
      - name: Print the result of the ansible.builtin.command module, using the ansible.builtin.debug module
        debug:
          var: icmp_ping_result
    
      - name: Print the results of the last two commands
        debug:
          msg:
          - "{{ ansible_ping_result }}"
          - "{{ icmp_ping_result }}"
    ```

15. Save the file by pressing [Esc], then [:]. Enter "wq" at the **":"** prompt.

16. Run the playbook:

    ```
    ansible-playbook ~/Ansible/fourth_playbook.yml
    ```

    - **Output:**

    ```
    PLAY [Fourth playbook] ********************************************************************************************************************************************************************************************
    
    TASK [Gathering Facts] ********************************************************************************************************************************************************************************************
    ok: [control]
    
    TASK [Ping the control node using the ansible.builtin.ping module, and save the result] ***************************************************************************************************************************
    ok: [control]
    
    TASK [Print the result of the ansible.builtin.ping module, using the ansible.builtin.debug module] ****************************************************************************************************************
    ok: [control] => {
        "ansible_ping_result": {
            "changed": false,
            "failed": false,
            "ping": "pong"
        }
    }
    
    TASK [Ping the control node using the ansible.builtin.command module and the Linux ping command, and save the result] *********************************************************************************************
    changed: [control]
    
    TASK [Print the result of the ansible.builtin.command module, using the ansible.builtin.debug module] *************************************************************************************************************
    ok: [control] => {
        "icmp_ping_result": {
            "changed": true,
            "cmd": [
                "ping",
                "-c",
                "4",
                "control"
            ],
            "delta": "0:00:03.064636",
            "end": "2023-01-17 23:30:06.656915",
            "failed": false,
            "msg": "",
            "rc": 0,
            "start": "2023-01-17 23:30:03.592279",
            "stderr": "",
            "stderr_lines": [],
            "stdout": "PING control (192.168.0.29) 56(84) bytes of data.\n64 bytes from control (192.168.0.29): icmp_seq=1 ttl=64 time=0.048 ms\n64 bytes from control (192.168.0.29): icmp_seq=2 ttl=64 time=0.083 ms\n64 bytes from control (192.168.0.29): icmp_seq=3 ttl=64 time=0.050 ms\n64 bytes from control (192.168.0.29): icmp_seq=4 ttl=64 time=0.056 ms\n\n--- control ping statistics ---\n4 packets transmitted, 4 received, 0% packet loss, time 3060ms\nrtt min/avg/max/mdev = 0.048/0.059/0.083/0.015 ms",
            "stdout_lines": [
                "PING control (192.168.0.29) 56(84) bytes of data.",
                "64 bytes from control (192.168.0.29): icmp_seq=1 ttl=64 time=0.048 ms",
                "64 bytes from control (192.168.0.29): icmp_seq=2 ttl=64 time=0.083 ms",
                "64 bytes from control (192.168.0.29): icmp_seq=3 ttl=64 time=0.050 ms",
                "64 bytes from control (192.168.0.29): icmp_seq=4 ttl=64 time=0.056 ms",
                "",
                "--- control ping statistics ---",
                "4 packets transmitted, 4 received, 0% packet loss, time 3060ms",
                "rtt min/avg/max/mdev = 0.048/0.059/0.083/0.015 ms"
            ]
        }
    }
    
    TASK [Print the results of the last two commands] *****************************************************************************************************************************************************************
    ok: [control] => {
        "msg": [
            {
                "changed": false,
                "failed": false,
                "ping": "pong"
            },
            {
                "changed": true,
                "cmd": [
                    "ping",
                    "-c",
                    "4",
                    "control"
                ],
                "delta": "0:00:03.064636",
                "end": "2023-01-17 23:30:06.656915",
                "failed": false,
                "msg": "",
                "rc": 0,
                "start": "2023-01-17 23:30:03.592279",
                "stderr": "",
                "stderr_lines": [],
                "stdout": "PING control (192.168.0.29) 56(84) bytes of data.\n64 bytes from control (192.168.0.29): icmp_seq=1 ttl=64 time=0.048 ms\n64 bytes from control (192.168.0.29): icmp_seq=2 ttl=64 time=0.083 ms\n64 bytes from control (192.168.0.29): icmp_seq=3 ttl=64 time=0.050 ms\n64 bytes from control (192.168.0.29): icmp_seq=4 ttl=64 time=0.056 ms\n\n--- control ping statistics ---\n4 packets transmitted, 4 received, 0% packet loss, time 3060ms\nrtt min/avg/max/mdev = 0.048/0.059/0.083/0.015 ms",
                "stdout_lines": [
                    "PING control (192.168.0.29) 56(84) bytes of data.",
                    "64 bytes from control (192.168.0.29): icmp_seq=1 ttl=64 time=0.048 ms",
                    "64 bytes from control (192.168.0.29): icmp_seq=2 ttl=64 time=0.083 ms",
                    "64 bytes from control (192.168.0.29): icmp_seq=3 ttl=64 time=0.050 ms",
                    "64 bytes from control (192.168.0.29): icmp_seq=4 ttl=64 time=0.056 ms",
                    "",
                    "--- control ping statistics ---",
                    "4 packets transmitted, 4 received, 0% packet loss, time 3060ms",
                    "rtt min/avg/max/mdev = 0.048/0.059/0.083/0.015 ms"
                ]
            }
        ]
    }
    
    PLAY RECAP ********************************************************************************************************************************************************************************************************
    control                    : ok=6    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
    ```

----

## Create a Remote Node

In this section, you will use a virtual remote node to test your Ansible playbooks.

1. Create a virtual machine, named *"ansible_remote"*, per the instructions in [Create the Virtual Machine](#create-the-virtual-machine). However, ensure the virtual machine has:

   - At least two (2) CPUs.
   - At least 2048 MB RAM.
   - At least 20 GB of hard drive space.

   > **NOTE** - To speed up the process, you can also ***clone*** the control node, and rename it *"ansible_remote"*:
   >
   > ![Clone Virtual Machine](ansible_tutorial_01.png "Clone Virtual Machine")
   > 
   > However:
   >
   > - For the **MAC Address Policy**, ensure you select `Generate new MAC addresses for all network adapters`.
   > - In addition, after cloning is complete, reduce the required RAM to **2048 MB**.
   >
   > For more information about cloning, see https://docs.oracle.com/en/virtualization/virtualbox/6.1/user/Introduction.html#clone.

2. Prepare the remote node, per the instructions in [Prepare the Control Node](#prepare-the-control-node). However, replace "remote" with "control" in all instances.

   > **NOTE** - If you cloned *ansible_control*, once you have rebooted the remote node:
   > 
   > - Log in using the remote user account.
   > - Clear out any "Welcome" dialog windows that may appear.
   > - Open a Terminal.
   > - Delete the control user account, using this command: `sudo userdel -frZ control`
   > - Reboot the remote node.

----

## Run Playbooks against the Remote Node

1. Edit the Ansible inventory file:

    ```
    sudo vim ~/Ansible/inventory.yml
    ```

2. Press [i], and add the remote node information to the file:

    ```
    ---
    
    control_nodes:
      hosts:
        control:
          ansible_host: <the control node IPv4 address>
          ansible_connection: ssh
          ansible_ssh_user: control
          ansible_ssh_pass: <the control node password>
   
    remote_nodes:
      hosts:
        remote:
          ansible_host: <the remote node IPv4 address>
          ansible_connection: ssh
          ansible_ssh_user: remote
          ansible_ssh_pass: <the remote node password>
    ```

3. Save the file by pressing [Esc], then [:]. Enter "wq" at the **":"** prompt.

4. Change the target nodes in the playbooks from `control` to `remote` using the stream editor command:

    ```
    # sed --in-place 's/hosts: control/hosts: remote/g' ~/Ansible/*_playbook.yml
    sudo sed -i 's/hosts: control/hosts: remote/g' ~/Ansible/*_playbook.yml
    ```

5. Run the first playbook and check for errors:

    ```
    ansible-playbook first_playbook.yml
    ```

    - **Output:**

    ```
    PLAY [First playbook] **********************************************************************************
    
    TASK [Gathering Facts] *********************************************************************************
    ok: [remote]
    
    TASK [Say Hello using the ansible.builtin.debug module] ************************************************
    ok: [remote] => {
        "msg": "Hello, World!"
    }
    
    PLAY RECAP *********************************************************************************************
    remote                     : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
    ```

6. Run the remaining playbooks and check for errors.

7. Change the target nodes in the playbooks from `remote` to `all` using the stream editor command:

    ```
    # sed --in-place 's/hosts: control/hosts: remote/g' ~/Ansible/*_playbook.yml
    sudo sed -i 's/hosts: control/hosts: remote/g' ~/Ansible/*_playbook.yml
    ```

8. Run all playbooks and check for errors.

----

## Install the Ansible Automation Platform

1. Download and install the Ansible Automation Platform Installer:

    ```
    sudo subscription-manager repos --enable=ansible-automation-platform-2.2-for-rhel-8-x86_64-rpms
    sudo yum -y install ansible-automation-platform-installer.noarch
    cd /opt/ansible-automation-platform/installer/
    sudo vim inventory
    ```

2. Make the following changes to the `inventory` file:

    ```
    [automationhub]
    control.example.net ansible_connection=local
    ...
    [all:vars]
    admin_password='<control password>'
    ...
    pg_password='<control password>'
    ...
    registry_username='<RedHat subscription username>'
    registry_password='<RedHat subscription password>'
    ...
    automationhub_admin_password='<control password>'
    ...
    automationhub_pg_password='<control password>'
    ```

3. Install the Ansible Automation Platform:

    ```
    sudo ./setup.sh
    ```

4. Open a browser and navigate to control.example.net. At the login screen, login with a username of **admin** and a password of **control**:

    > **NOTE** - Since you will be working with the GNOME Graphical User Interface (GUI) and Firefox, you may want to install the **GNOME Tweaks** application. This will allow you to customize the GUI to your preferences, such as restoring the Minimize and Maximize buttons in window title bars, etc.:
    >
    > ```
    > sudo subscription-manager repos --enable=rhel-8-for-x86_64-appstream-rpms
    > sudo dnf -y install gnome-tweaks
    > ```
    >
    > Press the **[Win]** key and enter *"tweaks"* to run the application.

---

## Notes

1. Ansible Tower and the Ansible Automation Platform (AAP) only run on Red Hat and CentOS Linux, and both require a Red Hat subscription.
2. You cannot run Ansible Tower or AAP on Fedora.
3. While the free and open source AlmaLinux and Rocky 8 operating systems are bug-for-bug compatible versions of RHEL 8, neither can run Ansible Tower nor AAP.
4. The Ansible command-line-interface (CLI) can run on most versions of Linux (including the Windows Subsystem for Linux), as long as Python 3.9 or greater is installed on the host.
5. Remote nodes can use most operating systems, including Debian, Windows, and macOS, and network device operating systems, such as Cisco, Palo Alto, etc.
