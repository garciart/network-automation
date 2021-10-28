import subprocess
import sys
from datetime import datetime

import pexpect

from cisco import Cisco
from labs import lab_utils


def main():
    """Application entry point

    :return: None
    :rtype: None
    """
    child = None
    try:
        print("Beginning lab...")
        c3745 = Cisco()
        for console_port_number in range(5000, 5005 + 1):
            if child:
                child.close()
            try:
                child = c3745.connect_via_telnet("192.168.1.1", console_port_number)
                break
            except RuntimeError:
                pass
        if not child:
            raise RuntimeError("Cannot connect via console port.")
        c3745.get_device_info(child)
        c3745.format_flash_memory(child)
        c3745.set_device_ip_addr(child, "192.168.1.20", "255.255.255.0")
        c3745.check_l3_connectivity(child, "192.168.1.10", "192.168.1.20")
        new_filename = "startup-config-{0}".format(datetime.utcnow().strftime("%y%m%d%H%M%SZ"))
        c3745.download_from_device_tftp(
            child,
            "startup-config",
            "192.168.1.10",
            new_filename)
        c3745.upload_to_device_tftp(
            child, "/var/lib/tftpboot/{0}".format(new_filename), "192.168.1.10", "flash:/startup-config.bak")
        c3745.update_startup_config(child)
        c3745.secure_privileged_exec_mode(child, "cisco")
        c3745.secure_console_port(child, "cisco")
        c3745.secure_auxiliary_port(child, "cisco")
        c3745.secure_virtual_teletype(child, "cisco")
        new_filename = "startup-config-{0}".format(datetime.utcnow().strftime("%y%m%d%H%M%SZ"))
        c3745.download_from_device_tftp(
            child,
            "startup-config",
            "192.168.1.10",
            new_filename)
        c3745.update_startup_config(child)
        c3745.close_telnet_conn(child)
        # child = c3745.connect_via_telnet("192.168.1.20")
        # REMOVE AFTER TESTING
        # c3745.upload_to_device_tftp(
        #     child, "/var/lib/tftpboot/startup-config", "192.168.1.10", "flash:/startup-config.bak")
        # c3745.restore_startup_config(child)
        # c3745.close_telnet_conn(child)

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
