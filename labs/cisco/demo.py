from cisco_ios import CiscoIOS
from labs.cisco.reporter import Reporter

reporter = Reporter()
switch = CiscoIOS('Switch')
eol = ''
child = switch.connect_via_telnet(reporter, eol,
                                  telnet_ip_addr='192.168.1.1',
                                  telnet_port_num=5000,
                                  verbose=True)

switch.set_switch_ip_addr(child, reporter, eol,
                          vlan_name='vlan 1',
                          vlan_port='GigabitEthernet0/0',
                          new_ip_address='192.168.1.20',
                          new_netmask='255.255.255.0',
                          commit=True)

switch.enable_ssh(child, reporter, eol,
                  label='DEMO',
                  modulus=1024,
                  version=1.99,
                  time_out=120,
                  retries=3,
                  commit=True)

switch.upload_to_device_scp(child, reporter, eol,
                            device_file_system='nvram',
                            remote_ip_addr='192.168.1.10',
                            remote_username='gns3user',
                            file_to_upload='/var/lib/tftpboot/switch-confg',
                            destination_filepath='startup-config',
                            remote_password='gns3user')

switch.reload_device(child, reporter, eol,
                     password='ciscon',
                     enable_password='cisen')

switch.close_telnet_connection(child, reporter)
