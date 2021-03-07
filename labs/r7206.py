#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test Script.
To run this lab:
* Start GNS3 by executing "./gn3_run.sh" in a Terminal window.
* Select Lab00 from the Projects library.
* Start all devices.

If Lab00 does not exist, follow the instructions in DEMO.md to create the lab.

Project: Automation

Requirements:
- Python 2.7.5
"""
from __future__ import print_function

import argparse
import logging
import os
import subprocess
import sys
import telnetlib
import time

import pexpect

from labs import CiscoRouter  # Super class!

# Enable error and exception logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(level=logging.NOTSET,
                    filename="labs.log",
                    format="%(asctime)sUTC: %(levelname)s:%(name)s:%(message)s")


class Ramon7206(CiscoRouter):
    @property
    def config_file_path(self):
        return self._config_file_path

    @property
    def device_ip_address(self):
        return self._device_ip_address

    @property
    def subnet_mask(self):
        return self._subnet_mask

    @property
    def host_ip_address(self):
        return self._host_ip_address

    def __init__(self, config_file_path, device_ip_address, subnet_mask, host_ip_address):
        self._device_ip_address = device_ip_address
        self._subnet_mask = subnet_mask
        self._config_file_path = config_file_path
        self._host_ip_address = host_ip_address

    def run(self, ui, **kwargs):
        try:
            ui.info("Hello from Cisco Ramon!")
            self._connect_to_device()
        except pexpect.exceptions.ExceptionPexpect:
            ex_type, ex_value, ex_traceback = sys.exc_info()
            ui.error("Type {0}: {1} in {2} at line {3}.".format(e_type.__name__,
                                                                ex_value,
                                                                ex_traceback.tb_frame.f_code.co_filename,
                                                                ex_traceback.tb_lineno))
        finally:
            ui.info("Good-bye from Cisco Ramon.")

    def _setup_host(self):
        pass

    def _connect_to_device(self):
        child = pexpect.spawn("telnet {0}".format(self._device_ip_address))

    def _setup_device(self):
        pass

    def _transfer_files(self):
        pass

    def _verify_device_configuration(self):
        pass


class Utility(object):
    TFTP_DIR = "/var/lib/tftpboot"

    def __init__(self):
        self.utility_user = "gns3_temp"
        self.utility_password = "567Eight"
        from datetime import date, timedelta

        # Ensure user expires even if the application crashes
        temp_expire = date.today() + timedelta(days=1)
        result = subprocess.call(["sudo", "-S", "useradd", "--system", "-p", self.utility_password, self.utility_user])
        if result != 0:
            raise RuntimeError(result + " Unable to create temporary system user.")

    def close_user(self):
        if subprocess.call(["sudo", "-S", "userdel", "-r", self.utility_user]) != 0:
            raise RuntimeError("Unable to delete temporary system user.")

    def pexpect_run_wrapper(self, cmd, timeout=30, error_message=None):
        pexpect.run
        child_result, child_exitstatus = pexpect.run(cmd, timeout=timeout, withexitstatus=True,
                                                     events={"(?i)password": "{0}\n".format(self.utility_password)})
        if child_exitstatus == 0:
            return child_result
        else:
            raise RuntimeError(error_message if error_message else child_result.decode("utf-8"))

    @staticmethod
    def pexpect_expect_wrapper(cmd, expected_result):
        pass

    def is_gns3_running(self):
        # Check if the gns3server process is running
        self.pexpect_run_wrapper("pgrep gns3server", error_message="GNS3 is not running. " +
                                                                   "Please run ./gns3_run.sh to start GNS3 before executing this script.")
        """
        child_result, child_exitstatus = pexpect.run("pgrep gns3server", timeout=30, withexitstatus=True)
        if child_exitstatus == 0:
            return child_result
        else:
            raise RuntimeError("GNS3 is not running. " +
                               "Please run ./gns3_run.sh to start GNS3 before executing this script.")
        """

    @staticmethod
    def is_the_lab_loaded(host_ip_address):
        try:
            # In Lab 0, the unconfigured router is connected to the host through console port 5001 TCP.
            with telnetlib.Telnet(host_ip_address, 5001):
                return True
        except ConnectionRefusedError:
            raise RuntimeError("Unable to reach device. " +
                               "Please load Lab 0 in GNS3 and start all devices before executing this script.")

    def enable_tftp(self):
        """This function:

        * Verifies the default TFTP directory exists (/var/lib/tftpboot) and it
          has the correct permissions
        * Enables the TFTP service, opens the firewall, and starts the TFTP server.

        :returns: True if the function succeeded or raises a RuntimeError.
        :rtype: bool
        """
        try:
            # Ensure tftpboot default folder exists and has the correct permissions
            # (i.e., 755+)
            dir_exists = os.path.isdir("/var/lib/tftpboot")
            if not dir_exists:
                ui_message.warning("tftpboot directory does not exist. Creating...")
                utility.pexpect_run_wrapper("sudo mkdir -p -m755" + self.TFTP_DIR)
            else:
                ui_message.info("Folder exists: Good to go...")
            dir_permissions = subprocess.check_output(["stat", "-c", "%a", self.TFTP_DIR])
            if int(dir_permissions) < 755:
                ui_message.warning("Incorrect permissions for tftpboot directory: Correcting...")
                utility.pexpect_run_wrapper("sudo chmod 755 " + self.TFTP_DIR)
            else:
                ui_message.info("Permissions correct: Good to go...")
            # Enable the TFTP service and start the TFTP server
            ui_message.info("Modifying the TFTP service configuration...")
            # subprocess.call(["sudo", "-S", "cp", "-f", os.getcwd() + "/tftp_on", "/etc/xinetd.d/tftp"])
            utility.pexpect_run_wrapper("sudo cp -f " + os.getcwd() + "/tftp_on /etc/xinetd.d/tftp", timeout=5)

            ui_message.info("Allowing TFTP traffic through firewall...")
            print(utility.pexpect_run_wrapper("sudo firewall-cmd --zone=public --add-service=tftp"))
            ui_message.info("Starting the TFTP server...")
            print(utility.pexpect_run_wrapper("sudo systemctl start tftp"))

            ui_message.info("TFTP service enabled.")
            ui_message.info("Don\"t forget to reset the TFTP service configuration before " +
                            "shutting down the machine!!!")
        except BaseException as ex:
            raise ex
        finally:
            utility.close_user()

    def disable_tftp(self):
        pass


class UserInterface(object):
    @staticmethod
    def info(msg):
        print("Message: {0}".format(msg))

    @staticmethod
    def debug(msg):
        print("Debug: {0}".format(msg))

    @staticmethod
    def warning(msg):
        print("Warning: {0}".format(msg))

    @staticmethod
    def error(msg):
        print("Error: {0}".format(msg))


if __name__ == "__main__":
    # To maintain scope, create empty class containers here
    ui_message = utility = r7206 = object()

    # Only catch errors and exceptions due to invalid inputs or incorrectly connected devices. Programming and logic
    # errors will be reported and corrected through user feedback
    try:
        # Instantiate the user interface messaging object here, since it does not have error-handling code
        ui_message = UserInterface()
        ui_message.info("Connecting to Cisco Ramon...")

        # Instantiate the utility object here, since it does not have error-handling code
        utility = Utility()

        # Check that GNS3 is running; if false, the method will raise an error and the script will exit.
        if utility.is_gns3_running() is not None:
            ui_message.info("GNS3 is running.")

        # Initialize default parameter values
        config_file_path = "test.cfg"
        device_ip_address = "192.168.1.10"
        subnet_mask = "255.255.255.0"
        host_ip_address = "192.168.1.100"

        # Get parameter values from the command-line
        parser = argparse.ArgumentParser()
        parser.add_argument("-x", "--execute", help="Run from the command line using the supplied parameter values. " +
                                                    "Requires config_file_path, device_ip_address, and subnet_mask.")
        parser.add_argument("--config_file_path",
                            help="The location of the configuration file to load into the router.")
        parser.add_argument("--device_ip_address",
                            help="The IP address for uploading the configuration file to the router.")
        parser.add_argument("--subnet_mask", help="The subnet mask that applies to the host and router. " +
                                                  "Default is {0}.".format(subnet_mask),
                            default=subnet_mask)
        parser.add_argument("--host_ip_address",
                            help="The IP address of the host. Default is {0}.".format(host_ip_address),
                            default=host_ip_address)
        args = parser.parse_args()

        if args.execute:
            # Replace default values with user-supplied values
            config_file_path = args.config_file_path
            device_ip_address = args.device_ip_address
            subnet_mask = args.subnet_mask if args.subnet_mask else subnet_mask
            host_ip_address = args.host_ip_address if args.host_ip_address else host_ip_address
        else:
            ui_message.warning("You are running this application with default test values.")

        # Instantiate the router object here, since __init__ does not have error-handling code
        r7206 = Ramon7206(config_file_path, device_ip_address, subnet_mask, host_ip_address)

        # Check if the lab is loaded and the device is started; if either is false, the method will raise an error
        # and the script will exit.
        if utility.is_the_lab_loaded(host_ip_address):
            ui_message.info("Lab 0 is loaded and started.")

        utility.enable_tftp()

    except (pexpect.exceptions.ExceptionPexpect, RuntimeError):
        # Format the error, report, and exit
        e_type, e_value, e_traceback = sys.exc_info()
        ui_message.error("Type {0}: '{1}' in {2} at line {3}.".format(e_type.__name__,
                                                                      e_value,
                                                                      e_traceback.tb_frame.f_code.co_filename,
                                                                      e_traceback.tb_lineno))
        ui_message.info("Good-bye.")
        exit(1)

    # The Ramon7206 object has its own error-handling code
    r7206.run(ui_message)
    ui_message.info("Script complete. Have a nice day.")
