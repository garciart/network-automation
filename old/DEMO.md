# Lab 00 - Demo

This demo/tutorial explains how to create a lab in GNS3 and how to use Python to configure a router.

>**Note** - If you are unfamiliar with GNS3, visit [https://docs.gns3.com/docs/using-gns3/beginners/the-gns3-gui/](https://docs.gns3.com/docs/using-gns3/beginners/the-gns3-gui/ "The GNS3 GUI") for a great introduction to the GNS3 Graphical User Interface (GUI).

1. Start GNS3 by opening a terminal and executing the "./gns3_run.sh" bash script.
2. When the **Project** window appears, select the **New Project** tab. Enter "Lab00" in the **Name** textbox and click **OK**. If the **Project** window does not appear, select **File -> New blank project** from the menu bar (on the top) or press **[CTRL]+[N]** .
   
![Create a New Project](../images/demo_01.png "Create a New Project")

3. In the **Devices Toolbar** (on the left), click on **New template**, or select **File -> New template** from the menu:

![Add a New Template - Step 1](../images/demo_02.png "Add a New Template - Step 1")

4. Select **Manually create a new template":

![Add a New Template - Step 2](../images/demo_03.png "Add a New Template - Step 2")

5. On the left, expand the **Dynamips** node and select **IOS routers**. When the right hand window appears, select **New** to add a template:  

![Add a New Template - Step 3](../images/demo_04.png "Add a New Template - Step 3")

6. Choose **New Image** and click **Browse**:

![Add a New Template - Step 4](../images/demo_05.png "Add a New Template - Step 4")

7. During setup, you should have downloaded a Cisco Internetwork Operating System (IOS) for both the Cisco 3745 Multiservice Access Router and the Cisco 7206VXR Router. Select "c7000-a3jk9s-mz.124-25d.bin" to use IOS 12.4(25) Mainline with the Cisco 7206VXR and click **Open** at the top:

>**Note** - If you do not have these files, you can download them manually from [http://tfr.org/cisco-ios/37xx/3745/c3745-adventerprisek9-mz.124-25d.bin](http://tfr.org/cisco-ios/37xx/3745/c3745-adventerprisek9-mz.124-25d.bin) and [http://tfr.org/cisco-ios/7200/c7200-a3jk9s-mz.124-25d.bin](http://tfr.org/cisco-ios/7200/c7200-a3jk9s-mz.124-25d.bin).

![Add a New Template - Step 5](../images/demo_06.png "Add a New Template - Step 5")

8. When asked to decompress the binary file into an IOS image, click **Yes**:

![Add a New Template - Step 6](../images/demo_07.png "Add a New Template - Step 6")

9. When you return to the IOS image selection window, click **Next**:

![Add a New Template - Step 7](../images/demo_08.png "Add a New Template - Step 7")

10. You can name the device whatever you like (e.g., "Cisco 7206", "My Router", etc.), but for now, accept the default values by clicking **Next**:

![Add a New Template - Step 8](../images/demo_09.png "Add a New Template - Step 8")

11. The minimum RAM for IOS 12.4(25) Mainline is 256 MiB, so accept the default value by clicking **Next**:

![Add a New Template - Step 9](../images/demo_10.png "Add a New Template - Step 9")

12. This device offers many configurations (e.g., additional FastEthernet ports, GigbitEthernet ports, etc.), but since we will only be using one port for this demo (FastEthernet0/0), accept the default values by clicking **Next**:

![Add a New Template - Step 10](../images/demo_11.png "Add a New Template - Step 10")

>**Note** - Here is a table of the configurations available for this device. For more information on additional configurations for the Cisco 7206, visit https://www.cisco.com/c/en/us/td/docs/routers/7200/configuration/7200_port_adapter_config_guidelines/config/3875In.html#wp1054974](https://www.cisco.com/c/en/us/td/docs/routers/7200/configuration/7200_port_adapter_config_guidelines/config/3875In.html#wp1054974 "Cisco 7200 Series Port Adapter Installation Requirements").

   |Product Number|Slot|Port Adapter Group|PA Type|
   |--------------|----|-----------------|-----|
   |C7200-IO-FE|0|I/O Controllers|1-port Fast Ethernet I/O controller (2 connectors: RJ-45 and MII)|
   |C7200-IO-2FE|0||2-port Fast Ethernet I/O controller|
   |C7200-IO-GE-E|0|I/O Controllers|1-port Gigabit Ethernet plus Ethernet I/O controller|
   |PA-A1|1-6|ATM|1-port multimode|
   |PA-FE-TX|1-6||1-port Fast Ethernet 100BASETX|
   |PA-2FE-TX|1-6|Ethernet/Fast Ethernet/Gigabit Ethernet|2-port Fast Ethernet (TX)|
   |PA-GE|1-6||1-port full-duplex Gigabit Ethernet|
   |PA-4T+|1-6|Serial|4-port synchronous serial, enhanced|
   |PA-8T|1-6|Serial|8-port synchronous serial|
   |PA-4E|1-6||4-port Ethernet 10BASET|
   |PA-8E|1-6||8-port Ethernet 10BASET|
   |PA-POS-OC3|1-6|SONET|1-port SFP module-based OC-3c/STM-1|

13. In order to prevent the Dynamips emulator from monopolizing resources and locking the system, you need to set an Idle-PC value. Click on **Idle-PC finder** to find a value:

![Add a New Template - Step 11a](../images/demo_12.png "Add a New Template - Step 11a")

![Add a New Template - Step 11b](../images/demo_13.png "Add a New Template - Step 11b")

>**Note** - Chris Welsh provides an excellent explanation of the Idle-PC value in his blog at [https://rednectar.net/2013/02/24/dynamipsgns3-idle-pc-explained-finally/](https://rednectar.net/2013/02/24/dynamipsgns3-idle-pc-explained-finally/ "Dynamips/GNS3 Idle-PC explained. Finally!").

14. When a value has been found, click **OK** to return to the Idle-PC window. Ensure the **Idle-PC** textbox contains the value, and then click **Finish**:

![Add a New Template - Step 12a](../images/demo_14.png "Add a New Template - Step 12a")

![Add a New Template - Step 12b](../images/demo_15.png "Add a New Template - Step 12b")

15. GNS3 will return you to the template window. Click **OK** to return to the **Workspace**.

![Project window](../images/demo_16.png)

16. In the **Devices Toolbar** (on the left), click on the **Browse all devices** icon and select **Cloud**:
   
![Project window](../images/demo_17.png)

19. Drag a cloud device into the **Workspace**. This is your host machine:

![Project window](../images/demo_18.png)

20. Select and drag a Cisco 3745 Multiservice Access Router (**c3745**) into the **Workspace**:

![Project window](../images/demo_19.png)

21. In the **Devices Toolbar** (on the left), click on the **Add a link** icon. Click on **Cloud1** and connect one end of the link to **tap0**:

![Project window](../images/demo_20.png)

22. Click on **R1** and connect the other end of the link to **FastEthernet0/0**:

![Project window](../images/demo_21.png)

>**Note** - To quickly identify nodes in the **Workspace**, click on the **Show/Hide interface labels** icon in the top **Toolbar**, or select **View -> Show/Hide interface labels** from the top menu.

23. Right click on **R1** and **Start** the device (You can also start all the devices using the green **Start** icon in the top **Toolbar**):

![Project window](../images/demo_22.png)

24. Right click on **R1** again to open a **Console**:

![Project window](../images/demo_23.png)

25. When the **Console** window appears, press **[Enter]** and wait for the prompt to appear:

![Project window](../images/demo_24.png)

>**Note** - If the prompt reads ```R1>```, you are in **User EXEC Mode**. Enter ```enable``` at the prompt to enter **Priviledged EXEC Mode** (i.e., ```R1>enable```).

26. Enter the following commands to reset the device (Press **[ENTER]** at the ```[confirm]``` prompts):

    
    R1#write erase
    Erasing the nvram filesystem will remove all configuration files! Continue? [confirm]
    [OK]
    Erase of nvram: complete
    R1#
    *Feb 24 03:42:43.875: %SYS-7-NV_BLOCK_INIT: Initialized the geometry of nvram
    R1#reload
    Proceed with reload? [confirm]
    
    *Feb 24 03:42:54.111: %SYS-5-RELOAD: Reload requested by console. Reload Reason: Reload Command.
    ROM: reload requested...

27. Close the **Console** window. Right click on **R1** again and **Stop** the device:
    
>**Note** - Normally, you would enter ```reload``` at the prompt to reload the device. However, do not do this; GNS3 may crash.

![Project window](../images/demo_25.png)

28. Right click on **R1** again and **Reload**. The device should start automatically:

![Project window](../images/demo_26.png)

29. Right click on **R1** again and reopen open a **Console**. This Cisco device stores its configuration settings in non-volatile RAM, known as NVRAM. Enter the following command to look at the contents of the NVRAM:

        R1#show startup-config
        Using 404 out of 155640 bytes!
        !
        !
        service timestamps debug datetime msec
        service timestamps log datetime msec
        no service password-encryption
        !
        hostname R1
        !
        ip cef
        no ip domain-lookup
        no ip icmp rate-limit unreachable
        ip tcp synwait 5
        no cdp log mismatch duplex
        !
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
        !
        !
        end
        
        R1#

30. Compare this to the running-config, which is built when the device starts and is stored in the device's volatile RAM:

        R1#show running-config
        Building configuration...
        
        Current configuration : 1932 bytes
        !
        version 12.4
        service timestamps debug datetime msec
        service timestamps log datetime msec
        no service password-encryption
        !
        hostname R1
        !
        boot-start-marker
        boot-end-marker
        !
        !
        no aaa new-model
        memory-size iomem 5
        no ip icmp rate-limit unreachable
        ip cef
        !
        !
        !
        !
        no ip domain lookup
        ip auth-proxy max-nodata-conns 3
        ip admission max-nodata-conns 3
        !
        !
        !
        !
        !
        !
        !
        !
        !
        !
        !
        !
        !
        !
        !
        !
        !
        !
        !
        ip tcp synwait-time 5
        ! 
        !         
        !
        !
        !
        interface FastEthernet0/0
         no ip address
         shutdown
         duplex auto
         speed auto
        !
        interface Serial0/0
         no ip address
         shutdown
         clock rate 2000000
        !
        interface FastEthernet0/1
         no ip address
         shutdown
         duplex auto
         speed auto
        !
        interface Serial0/1
         no ip address
         shutdown 
         clock rate 2000000
        !
        interface Serial0/2
         no ip address
         shutdown
         clock rate 2000000
        !
        interface FastEthernet1/0
         no ip address
         shutdown
         duplex auto
         speed auto
        !
        interface Serial2/0
         no ip address
         shutdown
         serial restart-delay 0
        !
        interface Serial2/1
         no ip address
         shutdown
         serial restart-delay 0
        !         
        interface Serial2/2
         no ip address
         shutdown
         serial restart-delay 0
        !
        interface Serial2/3
         no ip address
         shutdown
         serial restart-delay 0
        !
        interface FastEthernet3/0
        !
        interface FastEthernet3/1
        !
        interface FastEthernet3/2
        !
        interface FastEthernet3/3
        !
        interface FastEthernet3/4
        !
        interface FastEthernet3/5
        !
        interface FastEthernet3/6
        !
        interface FastEthernet3/7
        !
        interface FastEthernet3/8
        !
        interface FastEthernet3/9
        !
        interface FastEthernet3/10
        !
        interface FastEthernet3/11
        !
        interface FastEthernet3/12
        !
        interface FastEthernet3/13
        !
        interface FastEthernet3/14
        !
        interface FastEthernet3/15
        !
        interface Vlan1
         no ip address
        !
        ip forward-protocol nd
        !
        !
        no ip http server
        no ip http secure-server
        !
        no cdp log mismatch duplex
        !
        !
        !
        control-plane
        !
        !
        !
        !
        !
        !
        !
        !
        !
        !
        line con 0
         exec-timeout 0 0
         privilege level 15
         logging synchronous
        line aux 0
         exec-timeout 0 0
         privilege level 15
         logging synchronous
        line vty 0 4
         login
        !
        !
        end

31. 

R1#configure terminal ! Enter Global Configuration Mode
R1(config)#interface FastEthernet 0/0 ! Enter Interface Configuration Mode
R1(config-if)#ip address 192.168.1.10 255.255.255.0 ! Set the IP address of the router
R1(config-if)#no shutdown ! Bring up the interface
R1(config-if)#exit ! Exit Interface Configuration Mode
R1(config)# ip route 0.0.0.0 0.0.0.0 192.168.1.100 ! Configure the default gateway
R1(config)# end ! Exit Global Configuration Mode
R1#
*Mar  1 00:13:00.067: %SYS-5-CONFIG_I: Configured from memory by console

Ping the router’s default gateway:
Copy
R1# ping 192.168.1.100

Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 192.168.1.100, timeout is 2 seconds:
.!!!!
Success rate is 80 percent (4/5), round-trip min/avg/max = 32/36/40 ms
R1#

R1#write memory ! Save the new configuration to flash memory
Building configuration...
[OK]
R1#

Now look at the new and current configuration of the router
R1#show running-config
Building configuration...

Current configuration :
...
end

#R1

Compare to the startup configuration settings in the NVRAM:
#R1show startup-config
Using 1985 out of 155640 bytes
...
end

R1#

Now copy the current settings to the NVRAM. At the "Destination filename" prompt, press [ENTER] or input "startup-config":
R1#copy running-config startup-config
Destination filename [startup-config]?
Building configuration...
[OK]
R1#
