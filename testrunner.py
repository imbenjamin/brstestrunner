#!/usr/bin/python

from utils import TestrunnerUtils, RokuUtils

import sys
import getopt
import ipaddress
import time
import socket

verbose_mode = False
roku_ip = ""


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "i:hv", ["ip=", "help", "verbose"])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()
            sys.exit()
        elif opt in ("-v", "--verbose"):
            global verbose_mode
            verbose_mode = True
        elif opt in ("-i", "--ip"):
            global roku_ip
            roku_ip = arg

    print_welcome()

    # Check to see if IP is valid
    try:
        ipaddress.ip_address(roku_ip)
    except ValueError as err:
        print(err)
        sys.exit(2)

    # If dev channel is installed, start testing
    TestrunnerUtils.pretty_print("Checking that a dev channel app is installed...",
                                 TestrunnerUtils.TextDecorations.HEADER)
    if RokuUtils.RokuUtils(roku_ip).is_dev_installed():
        verbose_print("    OK")
        start_testing()
    else:
        TestrunnerUtils.pretty_print("ERROR: There doesn't seem to be a dev channel app installed!",
                                     TestrunnerUtils.TextDecorations.FAIL)
        sys.exit(1)


def start_testing():
    roku_utils = RokuUtils.RokuUtils(roku_ip)

    TestrunnerUtils.pretty_print("Starting testing...", TestrunnerUtils.TextDecorations.HEADER)

    # Go to HOME
    verbose_print("    Going to Home")
    roku_utils.keypress("Home")

    # Sleep 2 secs for device to settle
    time.sleep(2)

    # Launch dev channel
    verbose_print("    Launching dev channel app")
    roku_utils.launch_dev_channel()

    # Connect to telnet socket
    verbose_print("    Connecting to the Telnet interface on the Roku host...")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # TODO: Parameterise the Telnet timeout!
    s.settimeout(30)

    # connect to remote host
    try:
        s.connect((roku_ip, 8085))
    except socket.error as err:
        verbose_print("    Exception thrown: "+err.strerror)
        TestrunnerUtils.pretty_print("ERROR: Unable to connect to the Telnet interface on the Roku device!",
                                     TestrunnerUtils.TextDecorations.FAIL)
        sys.exit(1)

    verbose_print("        Connected to remote host.")
    verbose_print("    Reading Telnet output, please wait...")

    job_running = True
    received_lines = []
    while job_running:
        try:
            # Receive data from the socket
            data = s.recv(4096)
            if not data:
                # Host has terminated the connection
                TestrunnerUtils.pretty_print("ERROR: The connection was prematurely terminated by the host.",
                                             TestrunnerUtils.TextDecorations.FAIL)
                sys.exit(1)
            else:
                # Store the line
                received_lines.append(data.decode())
        except socket.timeout:
            # Socket has timed out, no more Telnet output is being received
            verbose_print("    No more Telnet output to read.")
            job_running = False
        except ConnectionError as err:
            # Some other ConnectionError has occurred
            verbose_print("    Exception thrown: "+err.strerror)
            TestrunnerUtils.pretty_print("ERROR: There was a problem with the connection.",
                                         TestrunnerUtils.TextDecorations.FAIL)
            job_running = False

    verbose_print("    Closing connection...")
    s.shutdown(socket.SHUT_RDWR)
    s.close()

    # TODO: Remove this print
    print("", "received_lines:", received_lines, "", sep="\r\n")


def print_welcome():
    print("",
          "********************************",
          "***  brstest testrunner 2.0  ***",
          "********************************",
          "",
          sep="\n")

    verbose_print("Verbose Mode is ON\n", TestrunnerUtils.TextDecorations.WARNING)


def print_usage():
    print("usage: " + sys.argv[0] + " --ip i [--verbose]",
          "    --ip i  IP address of the Roku device to test with",
          "    --verbose  Show more descriptive logging",
          "",
          "Example: " + sys.argv[0] + " --ip 192.168.1.78 --verbose",
          sep="\n")


def verbose_print(string, colour="", decoration=""):
    if verbose_mode:
        TestrunnerUtils.pretty_print(string, colour, decoration)


if __name__ == "__main__":
    main(sys.argv[1:])
