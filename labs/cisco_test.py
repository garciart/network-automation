import subprocess

import pexpect
from cisco import *
from labs import lab_utils


def main():
    """Application entry point

    :return: None
    :rtype: None
    """
    child = None
    try:
        print("Beginning lab...")
        # c3745 = Cisco()
        c3745 = Cisco("192.168.1.1", "192.168.1.10", "192.168.1.1", "255.255.255.0")

        """
        child = c3745.connect_via_telnet("192.168.1.1", 5002)
        c3745.get_device_info(child)
        c3745.format_device_memory(child)
        c3745.assign_device_ip_addr(child, "192.168.1.20", "255.255.255.0")
        c3745.check_l3_connectivity(child, "192.168.1.10", "192.168.1.20")
        c3745.download_file_tftp(child, "startup-config", "192.168.1.10", "start")
        c3745.close_telnet_conn(child)
        """

        child = c3745.connect_via_telnet(port_number=5002)
        c3745.get_device_info(child)
        c3745.format_device_memory(child)
        c3745.assign_device_ip_addr(child, "192.168.1.20")
        c3745.check_l3_connectivity(child)
        c3745.download_file_tftp(child, "startup-config", new_filename="sss")
        c3745.upload_file_tftp(child, "/var/lib/tftpboot/test.txt")
        c3745.close_telnet_conn(child)

    # Let the user know something went wrong and put the details in the log file.
    # Catch pexpect and subprocess exceptions first, so other exceptions
    # (e.g., BaseException, etc) do not handle them by accident
    except pexpect.ExceptionPexpect as pex:
        print(lab_utils.error_message(sys.exc_info(), pex=pex))
    except subprocess.CalledProcessError as cpe:
        print(lab_utils.error_message(sys.exc_info(), cpe=cpe))
    except Exception:
        print(lab_utils.error_message(sys.exc_info()))
    finally:
        if child:
            child.close()
        print("\n*** Restart the device before running this script again. ***\n")
        print("Script complete. Have a nice day.")


if __name__ == "__main__":
    main()
