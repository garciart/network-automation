from exercises.old.reconcile.old import Cisco

# Device connect to tap0
c = Cisco("Router", eol="")
child = c.connect_via_telnet("con", "192.168.1.1", 5001, verbose=False)
c.get_device_info(child)
# c.format_memory(child, disk_name="bootflash")
child.close()

# Device connect to tap0
c = Cisco("Switch", eol="")
child = c.connect_via_telnet("con", "192.168.1.1", 5003, verbose=False)
c.get_device_info(child)
c.format_memory(child, disk_name="flash0")
child.close()

# Cisco 3745 - R1 - flash - eol="\r"
# Cisco 7206 - R2 - disk0 - eol="\r"
# CiscoCSR1000v16.6.1-VIRL-1 - Router - bootflash - eol=""
# CiscoIOSvL215.2.1-1 - Switch - flash0 - eol=""

"""
# Device connect to tap0
c = Cisco("R1",
          vty_username="admin",
          vty_password="cisco",
          console_password="ciscon",
          aux_password="cisaux",
          enable_password="cisen")
# c.connect_via_serial()
child = c.connect_via_telnet("con", "192.168.1.1", 5001, verbose=True)
c.get_device_info(child)

c.format_memory(child)
c.set_device_ip_addr(child, "192.168.1.20", commit=True)
c.ping_from_device(child, "192.168.1.10")
c.ping_device("192.168.1.20")
c.secure_device(child,
                vty_username="admin",
                vty_password="cisco",
                privilege=15,
                console_password="ciscon",
                aux_password="cisaux",
                enable_password="cisen",
                commit=True)
sudo_password = "gns3user"
enable_ntp(sudo_password)
c.set_clock(child)
c.synch_clock(child, "192.168.1.10", commit=True)
c.set_device_hostname(child, "c3745")
c.set_device_hostname(child, "R1")
# disable_ntp(sudo_password)
c.close_telnet(child)
"""
