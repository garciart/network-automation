# -*- coding: utf-8 -*-
"""

"""
import hashlib
import os
import pipes
import re
import socket

__all__ = ('run_cli_command',
           'enable_tftp',
           'prep_for_tftp_download',
           'disable_tftp',
           'validate_ip_address',
           'validate_port_number',
           'validate_subnet_mask',
           'validate_file_path',
           'validate_switch_priority',
           'validate_username',
           'validate_password',
           'fix_tftp_filepath',
           'enable_ftp',
           'disable_ftp',)

import pexpect


def validate_ip_address(ip_address, ipv4_only=True):
    """Checks that the argument is a valid IP address. Causes an exception if invalid.

    :param str ip_address: The IP address to check.
    :param bool ipv4_only: If the method should only validate IPv4-type addresses.

    :return: None
    :rtype: None

    :raises ValueError: If the IP address is invalid.
    """
    if ip_address is not None and ip_address.strip():
        ip_address = ip_address.strip()
        try:
            socket.inet_pton(socket.AF_INET, ip_address)
        except socket.error:
            if ipv4_only:
                raise ValueError(
                    'Argument contains an invalid IPv4 address: {0}'.format(ip_address))
            else:
                try:
                    socket.inet_pton(socket.AF_INET6, ip_address)
                except socket.error:
                    raise ValueError(
                        'Argument contains an invalid IP address: {0}'.format(ip_address))
    else:
        raise ValueError('Argument contains an invalid IP address: {0}'.format(ip_address))


def validate_port_number(port_number):
    """Check if the port number is within range. Causes an exception if invalid.

    :param int port_number: The port number to check.

    :return: None
    :rtype: None

    :raises ValueError: if the port number is invalid.
    """
    if port_number not in range(0, 65535):
        raise ValueError('Invalid port number.')


def validate_subnet_mask(subnet_mask):
    """Checks that the argument is a valid subnet mask. Causes an exception if invalid.

    :param str subnet_mask: The subnet mask to check.
    :return: None
    :rtype: None
    :raises ValueError: if the subnet mask is invalid.

    .. seealso::
        https://codereview.stackexchange.com/questions/209243/verify-a-subnet-mask-for-validity-in-python
    """
    if subnet_mask is not None and subnet_mask.strip():
        subnet_mask = subnet_mask.strip()
        a, b, c, d = (int(octet) for octet in subnet_mask.split('.'))
        mask = a << 24 | b << 16 | c << 8 | d
        if mask < 1:
            raise ValueError('Invalid subnet mask: {0}'.format(subnet_mask))
        else:
            # Count the number of consecutive 0 bits at the right.
            # https://wiki.python.org/moin/BitManipulation#lowestSet.28.29
            m = mask & -mask
            right0bits = -1
            while m:
                m >>= 1
                right0bits += 1
            # Verify that all the bits to the left are 1's
            if mask | ((1 << right0bits) - 1) != 0xffffffff:
                raise ValueError('Invalid subnet mask: {0}'.format(subnet_mask))
    else:
        raise ValueError('Invalid subnet mask: {0}.'.format(subnet_mask))


def ping_from_host(destination_ip_addr, count=4, ):
    """Check connectivity with another device.

    :param str destination_ip_addr: IPv4 address of the other device.
    :param int count: Number of pings to send; limited to 32.
    :return: None
    :rtype: None
    """
    run_cli_command('ping -c {0} {1}'.format(count, destination_ip_addr))


def validate_file_path(filepath):
    """Check if the filepath exists. Causes an exception if invalid.

    :param str filepath: The filepath to check.
    :return: None
    :rtype: None
    :raises ValueError: if the filepath is invalid.
    """
    if not os.path.exists(filepath):
        raise ValueError('Invalid filepath.')


def validate_switch_priority(switch_priorities, min_priority=1, max_priority=15):
    """Checks that the switch priority value is valid.

    :param switch_priorities: The switch priority (int) or list of switch priorities to check.
    :param int min_priority: The minimum switch priority allowed on the switch.
    :param int max_priority: The maximum switch priority allowed on the switch.
        Currently, no switch manufacturers allow over 15
    :returns: None
    :rtype: None

    :raises ValueError: If the switch_priority is invalid.
    """
    if min_priority is None or max_priority is None or \
            not isinstance(min_priority, int) or not isinstance(max_priority, int) \
            or (1 > min_priority > max_priority) or min_priority < 1 or max_priority > 15:
        raise ValueError('Invalid switch priority range.')
    if not isinstance(switch_priorities, list):
        switch_priorities = [switch_priorities, ]
    for s in switch_priorities:
        if s is None or not isinstance(s, int) or s not in range(min_priority, max_priority + 1):
            raise ValueError('Argument contains an invalid switch priority: {0}'.format(s))


def validate_username(usernames):
    """Checks that the username is valid.

    :param usernames: The username (str) or list of usernames to check.
    :returns: None
    :rtype: None

    :raises ValueError: If the username is invalid.
    """
    if not isinstance(usernames, list):
        usernames = [usernames, ]
    for u in usernames:
        if u is None or not isinstance(u, basestring) or len(u.strip()) < 5:
            raise ValueError('Invalid username.')
        u = u.strip()
        if not bool(re.match('^[a-zA-Z0-9_.][a-zA-Z0-9_.-]*?$', u)):
            raise ValueError('Invalid characters may prevent username \'{0}\' '.format(u) +
                             'from being used as an SSH CLI argument.')


def validate_password(passwords):
    """Checks that a password is valid and contains no special characters.

    :param passwords: The password (str) or list of usernames to check.

    :returns: None
    :rtype: None

    :raises ValueError: If the username is invalid.
    """
    if not isinstance(passwords, list):
        passwords = [passwords, ]
    for p in passwords:
        if p is None or not isinstance(p, basestring) or len(p.strip()) < 5:
            raise ValueError('Invalid password.')
        p = p.strip()
        if not bool(re.match('^[a-zA-Z0-9_.][a-zA-Z0-9_.-]*?$', p)):
            raise ValueError('Invalid characters may prevent password \'{0}\' '.format(p) +
                             'from being used as an SSH CLI argument.')


def run_cli_command(command, sudo_password=None):
    """Runs OS commands. Exceptions must be handled by the instantiating module.
    This function uses pexpect instead of subprocess to simplify piping and redirection.

    :param command: The command to run through the CLI.
    :param str sudo_password: The superuser password to execute commands that require
        elevated privileges.

    :returns: The result of the command.
    :rtype: str
    :raises RuntimeError: If unable to execute the command.
    """

    # TEMP FOR TESTING #
    if sudo_password is None:
        sudo_password = 'gns3user'

    # TEMP FOR TESTING #
    command_output, exitstatus = pexpect.run(
        'sudo ' + command,
        events={'(?i)password': (sudo_password + '\r')},
        withexitstatus=True)
    if exitstatus != 0:
        # For Python 2.x, use string_escape.
        # For Python 3.x, use unicode_escape.
        # Do not use utf-8; Some characters, such as backticks, will cause exceptions
        raise RuntimeError(
            'Exit status: {0}: Unable to {1}: {2}'.format(
                exitstatus, command, command_output.decode('string_escape').strip()))
    return command_output.decode('string_escape').strip()


def enable_tftp(sudo_password=None):
    """List of commands to enable the Trivial File Transfer Protocol (TFTP) Service.

    :param str sudo_password: The superuser password to execute commands that require
        elevated privileges.

    :returns: None
    :rtype: None
    """
    commands = ['mkdir --parents --verbose /var/lib/tftpboot',
                'chmod 777 --verbose /var/lib/tftpboot',
                'systemctl start tftp',
                'firewall-cmd --zone=public --add-service=tftp',
                'firewall-cmd --zone=public --add-port=69/udp', ]
    for c in commands:
        run_cli_command(c, sudo_password)


def prep_for_tftp_download(placeholder_file_path, sudo_password=None):
    """Prepare PMA to accept a file for download via TFTP.

    **Note** - TFTP is very limited. TFTP can only copy to an existing file; it cannot create
    a new copy. Therefore, you must create a shell file for TFTP to copy data into, and give
    the shell the necessary permissions to accept the data.

    :param str placeholder_file_path: File to download. Path must start with /var/lib/tftpboot/.
    :param str sudo_password: The superuser password to execute commands that require
        elevated privileges.

    :returns: None
    :rtype: None

    :raises RuntimeError: If the file path does not start with /var/lib/tftpboot/.
    """
    if not placeholder_file_path.startswith('/var/lib/tftpboot/'):
        raise RuntimeError(
            'Bad file path: Use the default TFTP directory ' +
            '(ex. /var/lib/tftpboot/file_to_download.ext).')
    commands = ['touch {0}'.format(pipes.quote(placeholder_file_path)),
                'chmod 666 {0}'.format(pipes.quote(placeholder_file_path))]
    for c in commands:
        run_cli_command(c, sudo_password)


def fix_tftp_filepath(file_path):
    """Validate the filepath for the TFTP transfer and verify the source file
    exists. The TFTP configuration file sets the default TFTP directory,
    normally /var/lib/tftpboot (the equivalent of in.tftpd -s or
    --secure flag). Therefore, if the directory is also in the file path, it
    will appear twice (i.e., '/var/lib/tftpboot/var/lib/tftpboot/startup-config-c3745.tftp').
    The following code ensures that the file path contains only the necessary
    directory info to transfer the file.

    :param file_path: The raw file path.
    :type file_path: str

    :returns: The corrected file path

    :raises ValueError: If the file_path is invalid.
    """
    if file_path is not None and file_path.strip():
        file_path = file_path.strip()
        # Check if the file path was already modified
        # (i.e., it does not begin with 'var/lib/tftpboot/')
        default_dir_str = 'var/lib/tftpboot/'
        offset = file_path.rfind(default_dir_str)

        if offset != -1:
            # Default dir found in file path! Remove everything through the
            # last instance of /var/lib/tftpboot/
            # (e.g.,
            # /var/lib/tftpboot/startup-config-switch.tftp
            # becomes
            # startup-config-switch.tftp, etc.)
            offset += len(default_dir_str)
            file_path = file_path[offset:]
        else:
            # Check for and remove any leading forward slashes.
            # FYI - Not taking this step caused a lot of hate and
            # discontent towards the PMA!
            file_path = file_path if file_path[0] != '/' else file_path[1:]
        return file_path
    else:
        raise ValueError('Invalid file path.')


def disable_tftp(sudo_password=None):
    """List of commands to disable the Trivial File Transfer Protocol (TFTP) Service.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges.
    :returns: None
    :rtype: None
    """
    commands = ['firewall-cmd --zone=public --remove-port=69/udp',
                'firewall-cmd --zone=public --remove-service=tftp',
                'systemctl stop tftp', ]
    for c in commands:
        run_cli_command(c, sudo_password)


def enable_ftp(sudo_password=None):
    """List of commands to enable the Very Secure File Transfer Protocol Daemon (vsftpd)
    service.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges.
    :returns: None
    :rtype: None
    """
    commands = [
        'sudo sed --in-place \'/ftp_username=nobody/d\' /etc/vsftpd/vsftpd.conf',
        'sudo sed --in-place --expression \'$aftp_username=nobody\' /etc/vsftpd/vsftpd.conf',
        'sudo systemctl start vsftpd',
        'sudo firewall-cmd --zone=public --add-port=20/tcp',
        'sudo firewall-cmd --zone=public --add-port=21/tcp',
        'sudo firewall-cmd --zone=public --add-service=ftp', ]
    for c in commands:
        run_cli_command(c, sudo_password)


def disable_ftp(sudo_password=None):
    """List of commands to disable the Very Secure File Transfer Protocol Daemon (vsftpd)
    service.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges.
    :returns: None
    :rtype: None
    """
    commands = ['sudo firewall-cmd --zone=public --remove-service=ftp',
                'sudo firewall-cmd --zone=public --remove-port=21/tcp',
                'sudo firewall-cmd --zone=public --remove-port=20/tcp',
                'sudo sed --in-place \'/ftp_username=nobody/d\' /etc/vsftpd/vsftpd.conf',
                'sudo systemctl stop vsftpd', ]
    for c in commands:
        run_cli_command(c, sudo_password)


def enable_ssh(sudo_password=None):
    """List of commands to enable the Secure Shell (SSH) Protocol Service.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges.
    :return: None
    :rtype: None
    """
    commands = ['systemctl start sshd',
                'firewall-cmd --zone=public --add-service=ssh',
                'firewall-cmd --zone=public --add-port=22/tcp', ]
    for c in commands:
        run_cli_command(c, sudo_password)


def disable_ssh(sudo_password=None):
    """List of commands to disable Secure Shell (SSH) Protocol Service.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges.
    :return: None
    :rtype: None
    """
    commands = ['firewall-cmd --zone=public --remove-port=22/tcp',
                'firewall-cmd --zone=public --remove-service=ssh',
                'systemctl stop sshd', ]
    for c in commands:
        run_cli_command(c, sudo_password)


def set_utc_time(new_datetime, sudo_password=None):
    """Sets the system time without a connection to the Internet. Use before enabling the
    Network Time Protocol (NTP) Service for offline synchronization.

    **Note** - For maximum compatibility with devices, the timezone will be set UTC.

    :param str new_datetime: The desired UTC date and time, in 'YYYY-MM-DD HH:MM:SS' format.
    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the run_cli_commands() method.
    :return: None
    :rtype: None
    :raise RuntimeError: If the desired UTC date and time are in the wrong format.
    """
    import datetime
    try:
        datetime.datetime.strptime(new_datetime, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise RuntimeError('Invalid date-time format; expected \'YYYY-MM-DD HH:MM:SS\'.')
    try:
        commands = ['sudo timedatectl set-ntp false',
                    'sudo timedatectl set-timezone UTC',
                    'sudo timedatectl set-time \'{0}\''.format(new_datetime),
                    'sudo timedatectl set-local-rtc 0', ]
        for c in commands:
            run_cli_command(c, sudo_password)
    finally:
        run_cli_command(['sudo date --set \'{0} UTC\''.format(new_datetime), ],
                        sudo_password)


def enable_ntp(sudo_password=None):
    """List of commands to enable the Network Time Protocol (NTP) Service.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the run_cli_commands() method.
    :return: None
    :rtype: None
    """
    commands = ['sudo sed --in-place \'/server 127.127.1.0/d\' /etc/ntp.conf',
                'sudo sed --in-place \'/fudge 127.127.1.0 stratum 10/d\' /etc/ntp.conf',
                'sudo sed --in-place --expression \'$aserver 127.127.1.0\' /etc/ntp.conf',
                'sudo sed --in-place --expression \'$afudge 127.127.1.0 stratum 10\' /etc/ntp.conf',
                'sudo systemctl start ntpd',
                'sudo firewall-cmd --zone=public --add-port=123/udp',
                'sudo firewall-cmd --zone=public --add-service=ntp', ]
    for c in commands:
        run_cli_command(c, sudo_password)


def disable_ntp(sudo_password=None):
    """List of commands to disable the Network Time Protocol (NTP) Service.

    :param str sudo_password: The superuser password to execute commands that require
    elevated privileges. The user will be prompted for the password if not supplied
    during the call to the run_cli_commands() method.
    :return: None
    :rtype: None
    """
    commands = ['sudo sed --in-place \'/fudge 127.127.1.0 stratum 10/d\' /etc/ntp.conf',
                'sudo sed --in-place \'/server 127.127.1.0/d\' /etc/ntp.conf',
                'sudo firewall-cmd --zone=public --remove-service=ntp',
                'sudo firewall-cmd --zone=public --remove-port=123/udp',
                'sudo systemctl stop ntpd', ]
    for c in commands:
        run_cli_command(c, sudo_password)


def get_file_hash(filepaths):
    """Hash a file.

    :param list filepaths: The files to be hashed.
    :return: A dictionary of hashes for the file.
    :rtype: dict
    :raises ValueError: if the filepath mask is invalid.
    """
    if not isinstance(filepaths, list):
        filepaths = [filepaths, ]
    file_hashes = {}
    for f in filepaths:
        # noinspection PyTypeChecker
        if not os.path.exists(f):
            raise ValueError("Invalid filepath.")
        for a in hashlib.algorithms:
            try:
                h = hashlib.new(a)
                # noinspection PyTypeChecker
                h.update(open(f, "rb").read())
                file_hashes.update({a: h.hexdigest()})
            except ValueError:
                file_hashes.update({a: False})
    return file_hashes
