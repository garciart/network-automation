# Installing and Partitioning RHEL 8

**NOTE** - Also check out similar instructions for Rocky at https://docs.rockylinux.org/books/disa_stig/disa_stig_part1/!

I based this Red Hat Enterprise Linux (RHEL) installation and partitioning guide on the recommendations listed in [Performing a standard RHEL 8 installation, of the RHEL 8 Product Documentation](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html-single/performing_a_standard_rhel_8_installation), [Appendix E, *Partitioning reference*, of the Red Hat Enterprise Linux 8 System Design Guide](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/system_design_guide/partitioning-reference_system-design-guide) and the [Defense Information Systems Agency (DISA) Security Technical Implementation Guide (STIG)](https://ncp.nist.gov/checklist/980).

> **NOTE** - You can find additional security profiles and configurations at [*Guide to the Secure Configuration of Red Hat Enterprise Linux 8*, from the Open Security Content Automation Protocol (OpenSCAP) Security Guide](https://static.open-scap.org/ssg-guides/ssg-rhel8-guide-index.html).

This partitioning scheme will need at least 60 GiB of disk space, with 54 GiB of allocated space and 4 GiB of unallocated space, in case you need to resize a partition.

> **NOTE** - This is a basic partitioning scheme that is DISA STIG compliant. You can modify this partitioning to suit your needs. For example, if you are installing a web server, you can add additional partitions for `/var/log/httpd` (10 GiB STIG recommendation) and `/var/www/html` (No STIG recommendation on size).

> **NOTE** - Modern computers use the **Extensible Firmware Interface (EFI)**, instead of the original BIOS system, for boot up. If you are using a virtual machine hypervisor, and want to use the image to create installation ISO's, ensure the firmware type is set to **UEFI** (in VirtualBox, ensure **Enable EFI** is checked). However, if asked, do not enable Secure Boot.

You will also need an Internet connection and an active [Red Hat Developer account](http://access.redhat.management "Red Hat Developer account").

> **NOTE** - If you are using a virtual machine hypervisor, ensure you set your connection to **Bridged**, which will allow the VM to reach the Internet, and interact with the host and other VMs, such as through Secure Shell (SSH). In addition, once you apply the STIG to the VM, the system will disable any shared folders and cut-and-paste functionality, so you will need to use SSH transfer protocols, such as SFTP or SCP, to transfer files between the host and the VM.

1. When the installer starts, at the **Welcome** screen, select your language and click on **Continue**:

pic

2. At the **Installation Summary** screen, under **System**, select **Installation Destination**:

pic

3. At the  **Installation Destination** screen, change the **Storage Configuration** to **Custom**, and click on **Done**:

pic

4. The **Manual Partitioning** screen wil appear:

pic

5. Add the following mount points, by clicking on **+**, filling the appropriate textboxes, and clicking on **Add mount point**:

pic

   > **NOTE** - These partitions and sizes are based on the [RHEL 8 Recommended partitioning scheme] (https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html-single/performing_a_standard_rhel_8_installation/index#recommended-partitioning-scheme_partitioning-reference "Performing a standard RHEL 8 installation") and the Defense Information Systems Agency (DISA) Security Technical Implementation Guide (STIG):
   >
   > - SV-214262r612240_rule - The Apache web server must use a logging mechanism that is configured to allocate log record storage capacity large enough to accommodate the logging requirements of the Apache web server.
   > - SV-214290r612241_rule - The Apache web server document directory must be in a separate partition from the Apache web servers system files.
   > - SV-230292r627750_rule - RHEL 8 must use a separate file system for /var.
   > - SV-230293r627750_rule - RHEL 8 must use a separate file system for /var/log.
   > - SV-230294r627750_rule - RHEL 8 must use a separate file system for the system audit data path.
   > - SV-230295r627750_rule - A separate RHEL 8 filesystem must be used for the /tmp directory.
   > - SV-230328r627750_rule - A separate RHEL 8 filesystem must be used for user home directories (such as /home or an equivalent).
   > - SV-230476r854040_rule - RHEL 8 must allocate audit record storage capacity to store at least one week of audit records, when audit records are not immediately sent to a central audit record storage facility.
   > - SV-244529r743836_rule - RHEL 8 must use a separate file system for /var/tmp.

   | Mount Point:   | Desired Capacity: | Group: | Total: | Notes:                                                                          |
   | -------------- | :---------------: | ------ |:-----: | ------------------------------------------------------------------------------- |
   | /              | 20 GiB            | System | 10 GiB | RHEL recommendation is 10 GiB, but you will need more to create an bootable ISO |
   | /boot          | 1 GiB             | System | 11 GiB | RHEL recommendation                                                             |
   | /boot/efi      | 200 MiB           | System | 11.2 GiB | RHEL recommendation                                                             |
   | /home          | 1 GiB             | Data   | 12.2 GiB | RHEL and STIG recommendation                                                    |
   | /var           | 3 GiB             | System | 15.2 GiB | STIG recommendation                                                             |
   | /var/log       | 5 GiB             | Data   | 20.2 GiB | STIG recommendation                                                             |
   | /var/log/audit | 10 GiB            | Data   | 30.2 GiB | STIG recommendation                                                             |
   | /var/tmp       | 1 GiB             | Data   | 31.2 GiB | STIG recommendation                                                             |
   | swap           | 4 GiB             | System | 35.2 GiB | Based on the system's RAM. See [Appendix E, *Partitioning reference*, of the RHEL 8 System Design Guide](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/system_design_guide/partitioning-reference_system-design-guide), for details |
   | /tmp           | 1 GiB             | System | 36.2 GiB | STIG recommendation                                                             |
   | /usr           | 10 GiB            | System | 46.2 GiB | RHEL recommendation (5 GiB w/o a GUI)                                           |

   You should have approximately 3.8 GiB of available space remaining after adding the partitions.

pic

6. Once you have created the partitions, select each one, with the exception of `/boot` and `/boot/efi`, and ensure their **Device Type** is **LVM** and the **Encrypt** checkbox is selected:

   > **NOTE** - This actions satisfies DISA STIG SV-230224r809268_rule, *All RHEL 8 local disk partitions must implement cryptographic mechanisms to prevent unauthorized disclosure or modification of all information that requires at rest protection*.

pic

   Click on **Update Settings** to commit the change.

7. Click on **Done** when finished. The **Disk Encryption Passphrase** dialog will appear:

pic

8. Enter a STIG-compliant passphrase:

   - 15 characters.
   - At least one uppercase, lowercase, number, and special character (use dashes (-), periods (.), or underscores ( ) only, to avoid using reserved special characters, such as operators (|), comment identifiers (#, !, etc.), or email address delimiters (@), which may cause transfers to fail).
   - No more than 4 characters of the same type consecutively.

pic

   Click on **Save Passphrase** when finished.

9. The **Summary of Changes** dialog will appear. If everything is correct, click on **Accept Changes**:

pic

10. When you return to the **Installation Summary** screen, under **System**, select **KDUMP**:

pic

11. Uncheck the **Enable kdump** checkbox, then click on **Done**:

    > **NOTE** - This actions satisfies DISA STIG SV-230310r627750_rule, RHEL 8 must disable kernel dumps unless needed.
	
pic

12. When you return to the **Installation Summary** screen, under **User Settings**, select **Root Password**:

pic

13. When the **Root Password** screen appears, enter a **temporary** passphrase. When you apply the STIG, the system will ask you to change your password when you first log in:

    > **NOTE** - Disregard any warnings stating that your temporary passphrase failed a check; you will change it to a STIG-compliant password when you first log in. Click on **Done** twice to confim the temporary passphrase.

pic

    Click on **Done** when finished.

14. When you return to the **Installation Summary** screen, under **User Settings**, select **User Creation**:

pic

15. When the **Create User** screen appears:

    - Enter your choice of a **Full name** and **User name**.
	- Ensure both the **Make this user administrator** and **Require a password to use this account** checkboxes are checked.
	- Enter a **temporary** passphrase. When you apply the STIG, the system will ask you to change your password when you first log in:

    > **NOTE** - Disregard any warnings stating that your temporary passphrase failed a check; you will change it to a STIG-compliant password when you first log in. Click on **Done** twice to confim the temporary passphrase.

    Click on **Done** when finished.

    > **NOTE** - To add the user to other groups (vboxsf, etc.), you can click the **Advanced** button and add the group to the account. You can also do it manually later on, using the following command:
	>
	> pic
	>
	> ```
	> sudo usermod -aG vboxsf <user name>
	> ```

pic

15. When you return to the **Installation Summary** screen, under **System**, select **Security Policy**:

pic

16. At the **Security Policy** screen, scroll thorugh the available profiles and click on the **DISA STIG with GUI for Red Hat Enterprise Linux**:

pic

17. Click on **Select Profile**. Look at the **Changes that were done or need to be done** listing; the system will make these changes during installation, so the system complies with the DISA STIG:

pic

    Click on **Done** when finished.

18. To implement the security policy during installation and perform updates, you need an active [Red Hat Developer account](http://access.redhat.management "Red Hat Developer account"). However, you must first onfigure your network connection. Once you return to the **Installation Summary** screen, under **System**, select **Network and Host Name**.

pic

19. At the **Network and Host Name** screen, select your Ethernet controller and turn it on. 

pic

    > **NOTE** - You can also change your host name, from the default and generic `localhost.localdomain`, to something more intuitive, such as `r8-stig-gui.dev`. Remember, the host name should only contain lower case alphanumeric characters and hyphens.

pic

    > **NOTE** - Depending on your organization's requirements, you may have to modify your network connection, such as adding a static IPv4 connection. However, for this tutorial, continue to use the Dynamic Host Configuration Protocol (DHCP) service.
	
pic

    Take note of the controller's IPv4 address (you can use it later to connect to the VM via Secure Shell (SSH)), and click on **Done** when finished.

20. Once you return to the **Installation Summary** screen, under **Software**, select **Connect to Red Hat**.

pic

21. Enter your Red Hat credentials you use to access your subscription. You may also check **Set System Purpose** and enter the system's role, software licensing agreement (SLA) type, and how you will use the system.

pic

    Click on **Register**. After a few minutes, the wizard will let you know the system has been properly subscribed.
	
	> **NOTE** - If you do not have an Internet connection or you do not want to register at this time, you can register later, using the following commands.
	
	```
    sudo subscription-manager register --username <Red Hat subscription username>
    sudo subscription-manager refresh
    sudo subscription-manager auto-attach --enable
    ```

pic

    > **NOTE** - You can check if the system was registered at https://access.redhat.com/management/systems.

	Click on **Done** when finished.

Under **Software**, select **Installation Source**:
At the **Installation Source** screen, change from **Red Hat CDN** to **Auto-detected installation media**:
Click **Verify**:
Wait for the **Media Verification** dialog to finish:
Click **Done** to close the dialog:
Click **Done** to return to the **Installation Summary** screen:
Wait for the wizard to update the screen:
Under **Software**, select **Software Selection**:
At the **Software Selection** screen, ensure only **Server with GUI** is selected:
Click on **Done** when finished:

17. Once you return to the **Installation Summary** screen, continue to customize the installation, per your organization's requirements, such as adding more users, language support, etc.

18. Once you are finished customizing the installation, click on **Begin Installation**.

19. The **Installation Progress** screen will appear and the installation will start.

20. Once the installation is complete, click on **Reboot System**.

21. After the system reboots, the **Linux Unified Key Setup (LUKS)** login screen will appear. Enter the passphrase you created during installation to continue.

    > **NOTE** - This passphrase textbox will capture all input and cannot be bypassed. You cannot and do not need to place a mouse cursor within the text box to enter text.

22. At the **Initial Setup** screen, under **Licensing**, click on **License Information**.

23. The **License Information** screen will appear. Once you have finished reading the License Agreement, check the **I accept the license agreement** checkbox, then click on **Done** to continue.

24. Click on **Finish Configuration** to continue.

25. The system will finish the boot process and the user selection screen will appear. Click on your user.

Enter your temporary password in the **Password** textbox and click on **Sign In**.

A message will appear, informing you that you need to change your password. However, once again, enter the temporary password in the **Current password** textbox, and click on **Sign In**.

Enter a new STIG-compliant password in the **New password** textbox and click on **Sign In**.

   - 15 characters.
   - At least one uppercase, lowercase, number, and special character (use dashes (-), periods (.), or underscores ( ) only, to avoid using reserved special characters, such as operators (|), comment identifiers (#, !, etc.), or email address delimiters (@), which may cause transfers to fail).
   - No more than 4 characters of the same type consecutively.

Reenter the new password and click on **Sign In**.

Once complete, the **Welcome** screen will appear. Click on **Next** to continue.

26. At the **Privacy** screen, set **Location Services** to off, then click on **Next** to continue.

27. At the **Online Accounts** screen, click on **Skip** to continue.

28. If you did not create a user during installation, you will be prompted to do so now. Follow the instructions to create a user and add a password. (need screenshots)

    > **NOTE** - The system will assign this user to the **wheel** group, making the user an administrator, with **sudo** privileges.

29. At the **Ready to Go** screen, click **Start Using Red Hat Enterprise Linux** to continue.

30. Close the **Getting Started** screen when it appears.

31. Access your applications by clicking on the **Activities** menu or pressing the **Super** key. Open a Terminal by entering "Terminal" in the textbox and pressing **[Enter**], or clicking on the Terminal icon on the left.

32. Update your system using the following commands; enter your password when prompted (this may take a while):

    ```
    sudo yum -y update
    sudo yum -y upgrade
    sudo yum -y clean all
    sudo yum -y autoremove
    ```

    >**NOTE** - Once you apply the STIG to the VM, the system will disable any shared folders and direct cut-and-paste functionality. However, you can connect to the VM using Secure Shell (SSH) and the command line or application, such as PuTTY, etc.

33. Install the Open SCAP (Security Content Automation Protocol) scanner and SCAP security documents from the National Institute of Standards and Technology (NIST); they may already be installed:

    ```
    sudo yum -y install openscap-scanner scap-security-guide
    ```

34. List all the available security profiles:

    ```
    ls /usr/share/xml/scap/ssg/content
    ```

35. Display information about a security profile; this command will *fetch* the profile if it is not present:

    ```
    oscap info --fetch-remote-resources /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml
    ```

36. To run the OpenSCAP scans correctly, you must be **root**. Switch to the **root** user account:

```
su -
```

Enter your temporary password at the prompt and press **[Enter]**.

A message will appear, informing you that you need to change your password. However, once again, enter the temporary password at the prompt and press **[Enter]**.

Enter a new STIG-compliant password at the **New password** prompt and press **[Enter]**.

   - 15 characters.
   - At least one uppercase, lowercase, number, and special character (use dashes (-), periods (.), or underscores ( ) only, to avoid using reserved special characters, such as operators (|), comment identifiers (#, !, etc.), or email address delimiters (@), which may cause transfers to fail).
   - No more than 4 characters of the same type consecutively.

Reenter the new password and press **[Enter]**.

The username in the prompt will chnage to **root**.

36. Run a scan using the eXtensible Configuration Checklist Description Format (XCCDF) **eval** module:

    > **NOTE** - For more information about scanning or using other formats, such as OVAL, see https://static.open-scap.org/openscap-1.3/oscap_user_manual.html#_scanning.

    ```
    oscap xccdf eval --report scan_report_1.html --results scan_results_1.xml --profile stig_gui /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml
    ```

37. View the report:

    ```
    chmod 644 scan_re*
    firefox scan_report_1.html
    ```

38. Scroll down to the **Compliance and Scoring** section. In this case, it looks like, out of 378 conditions, your system did not meet the contitions of 47 rules. However, do not panic!

To view details, click on the rule.

Scroll down for details.

In this case, the scanner says that the following line is missing from the `/etc/crypto-policies/back-ends/gnutls.config` file:

```
+VERS-ALL:-VERS-DTLS0.9:-VERS-SSL3.0:-VERS-TLS1.0:-VERS-TLS1.1:-VERS-DTLS1.0
```

However, when you view the `gnutls.config` file, you will see that the line is there, ut not in the same order:

```
+VERS-ALL:-VERS-DTLS0.9:-VERS-TLS1.1:-VERS-TLS1.0:-VERS-SSL3.0:-VERS-DTLS1.0:
```

The scanner uses regular expressions to check files, and the regex patterns may not always match up. This is one reason why it is important to review each item before issuing out a operating system build.

In addition, there are cases where you do not want to enforce a rule, or at least enforce it right away.


In this example, the **McAfee Endpoint Security for Linux (ENSL)** package required a subscription, which you may not want to pay for until the operating system is installed.

Continue to look through the report, and lose the browser when you are finished, by clicking the **[X]** in the top right corner.

39. There are several ways to fix compliance problems:

Create and use a Bourne Again Shell (BASH) remediation script:

```
oscap xccdf generate fix --output scan_remediate_1.sh --profile stig_gui scan_results_1.xml
```

Create and use an Ansible remediation script:

```
oscap xccdf generate fix --fix-type ansible --output scan_remediate_1.yml --profile stig_gui scan_results_1.xml
```

However, since you will not install Anisble on this system, run the BASH script.

```
chmod 755 scan_remediate*
bash scan_remediate_1.sh
```

The system may restart. Login using your user account, not the root account.

Run the scan again, but change the name of the report and results files.

    ```
    oscap xccdf eval --report scan_report_2.html --results scan_results_2.xml --profile stig_gui /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml
    ```

37. View the report:

    ```
    chmod 644 scan_re*
    firefox scan_report_2.html
    ```

38. Scroll down to the **Compliance and Scoring** section. In this case, it looks like you reduced the number of violations to 36. Go through them, starting with the high severity issues.


Either attempt to remediate the problems or document why they are allowed to exist. Once you have finished reviewing the STIG, you can use this setup for future installations.
