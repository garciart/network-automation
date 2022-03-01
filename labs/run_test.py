from labs.cisco import Cisco
from labs.utility import enable_ntp, disable_ntp

c = Cisco("R1",
          vty_username="admin",
          vty_password="cisco",
          console_password="ciscon",
          aux_password="cisaux",
          enable_password="cisen")
# c.connect_via_serial()
child = c.connect_via_telnet("192.168.1.1", 5001, verbose=True)
c.format_memory(child)
c.get_device_info(child)
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
disable_ntp(sudo_password)
c.close_telnet(child)
