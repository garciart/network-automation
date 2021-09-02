#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test
"""
from __future__ import print_function

import subprocess
import sys

import pexpect

if __name__ == "__main__":
    temp_user = "gns3_temp"
    try:
        # Create password and encrypt for temporary user
        import random
        import string

        password_characters = string.ascii_letters + string.digits
        user_password = ''.join(random.choice(password_characters) for _ in range(8))
        cmd = "openssl passwd -crypt {0}".format(user_password)

        import shlex

        crypt_password = subprocess.check_output(shlex.split(cmd)).strip().decode("utf-8")
        if crypt_password:
            print("Random password generated: {0}".format(user_password))
        else:
            raise RuntimeError("Unable to generate a random password.")

        # Ensure user expires even if the application crashes
        from datetime import date, timedelta

        temp_expire = str(date.today() + timedelta(days=1))
        # Use subprocess here, so the user running the script, if not root, gets prompted for their password
        cmd = "sudo -S useradd --system --expiredate {0} --password {1} {2}".format(
            temp_expire, crypt_password, temp_user)
        result = subprocess.call(shlex.split(cmd))
        if result == 0:
            print("Temporary system user account created.")
        else:
            raise RuntimeError("Unable to create temporary system user.")

        # Switch to temporary account
        cmd = "su - {0}".format(temp_user)

        child_result, child_exitstatus = pexpect.run(cmd, timeout=5, withexitstatus=True,
                                                     events={"(?i)Password": "{0}\n".format(user_password)})
        if child_exitstatus == 0:
            print("Switched to temporary system user account.")
        else:
            raise RuntimeError(
                "Unable to switch to temporary system user account: {0}".format(child_result.decode("utf-8")))

        cmd = "sudo whoami"
        subprocess.call(shlex.split(cmd))
    except (BaseException, subprocess.CalledProcessError):
        ex_type, ex_value, ex_traceback = sys.exc_info()
        print("Type {0}: {1} in {2} at line {3}.".format(ex_type.__name__,
                                                         ex_value,
                                                         ex_traceback.tb_frame.f_code.co_filename,
                                                         ex_traceback.tb_lineno))
    finally:
        # subprocess.call(["exit"])
        subprocess.call(["sudo", "-S", "userdel", "-f", temp_user])
