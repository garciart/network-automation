# Windows Instructions

[https://docs.gns3.com/docs/getting-started/installation/windows/](https://docs.gns3.com/docs/getting-started/installation/windows/ "GNS3 Windows Install")

[https://www.youtube.com/watch?v=Ibe3hgP8gCA&list=PLhfrWIlLOoKNFP_e5xcx5e2GDJIgk3ep6&index=1&ab_channel=DavidBombal](https://www.youtube.com/watch?v=Ibe3hgP8gCA&list=PLhfrWIlLOoKNFP_e5xcx5e2GDJIgk3ep6&index=1&ab_channel=DavidBombal "GNS3 Installation - David Bombal")

Graphical Network Simulator-3
Create a GNS3 account
Download the GNS3 installer for Windows (2.2.13)
Install GNS3:

Check out https://www.sysnettechsolutions.com/en/configure-loopback-adapter-in-gns3/

Run the Add Hardware Wizard (hdwwiz.exe) as Administrator
Network Adapters -> Microsoft -> Microsoft KM-TEST loopback adapter
Open the Control Panel
Visit Control Panel\Network and Internet\Network Connections
Rename the Microsoft KM-TEST loopback adapter to "LoopbackEth"
DO NOT ADD THE STATIC IP ADDRESS
Restart computer

Open the GNS3 application
Select icon to "Browse End Devices" from far left window
Select and drag a cloud into the workspace (GNS3 will name it Cloud1)
Node -> Configure
Check "Show special Ethernet interfaces"
Select LoopbackEth from dropdown list and click Add 
Select LoopbackEth from Ethernet Interfaces textbox and click OK

Download c3745-adventerprisek9-mz.124-25d.bin from the router images at http://tfr.org/cisco/

(for linux: wget http://tfr.org/cisco/7200/c7200-advipservicesk9-mz.124-24.T5.bin)

File -> New Template
"Install an appliance from the GNS3 server (recommended)" -> "Next >"
Routers -> Cisco 3745 -> Install
"Install the appliance on your local computer"  -> "Next >"
Check "Allow custom files"
Click "Yes" when asked "Do you want to proceed?"
Expand "3745 version 124-25d" node and select "c3745-adventerprisek9-mz.124-25d.image"
Click Import
Locate and select downloaded binary file -> Open
Click "Yes" when asked "Do you want to accept it at your own risks?"
Wait until the import is complete and click "Next >"
Click "Yes" when asked "Would you like to install Cisco 3745 version 124-25d?"
Wait until the import is complete and click "Finish"
Click "OK" to close the "Add template" popup. If any errors occurred, please repeat the steps.

Add appliance (router R0)
Select and start appliance
Look up R0's console port (should be localhost:5000)
Connect Cloud1's LoopbackEth to R0 FastEthernet0/0
Opened a Command window (cmd or Powershell)
Input "telnet localhost 5000" to connect to R0

Press return and configure R0
Press Ctrl + "]" to leave R0.
Input "q" to exit telnet.
