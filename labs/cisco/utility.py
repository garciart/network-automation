# -*- coding: utf-8 -*-
"""

"""
import os
import pipes
import re
import socket

__all__ = ['validate_ip_address', 'validate_subnet_mask', 'validate_port_number',
           'validate_filepath', 'validate_username', 'validate_password',
           'run_cli_command', 'fix_tftp_filepath', 'prep_for_tftp_download',
           'enable_tftp', 'disable_tftp', ]

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


def validate_filepath(filepath):
    """Check if the filepath exists. Causes an exception if invalid.

    :param str filepath: The filepath to check.
    :return: None
    :rtype: None
    :raises ValueError: if the filepath is invalid.
    """
    if not os.path.exists(filepath):
        raise ValueError('Invalid filepath.')


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
