#!/usr/bin/python

import getopt
import os.path as path
import re
import socket
import sys
import time

from utils import TestrunnerUtils, RokuUtils

verbose_mode = False
roku_ip = ""
out_dir = "./"
out_name = "report"


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "i:d:n:hv", ["ip=", "outdir=" "help", "verbose"])
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
            try:
                socket.inet_aton(arg)
            except socket.error as err:
                verbose_print("    Exception thrown: "+str(err))
                TestrunnerUtils.pretty_print("ERROR: The IP Address given is not valid!",
                                             TestrunnerUtils.TextDecorations.FAIL)
                sys.exit(2)
            else:
                global roku_ip
                roku_ip = arg
        elif opt in ("-o", "--outdir"):
            if path.isdir(arg):
                global out_dir
                out_dir = arg
            else:
                TestrunnerUtils.pretty_print("ERROR: The output directory given is not valid!",
                                             TestrunnerUtils.TextDecorations.FAIL)

    if roku_ip == "":
        TestrunnerUtils.pretty_print("ERROR: Missing required arguments", TestrunnerUtils.TextDecorations.FAIL)
        print_usage()
        sys.exit(2)

    print_welcome()

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

    receiving_output = True

    telnet_output = []
    while receiving_output:
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
                telnet_output.append(data.decode())
        except socket.timeout:
            # Socket has timed out, no more Telnet output is being received
            verbose_print("    No more Telnet output to read.")
            receiving_output = False
        except Exception as err:
            # Some other ConnectionError has occurred
            verbose_print("    Exception thrown: "+str(err))
            TestrunnerUtils.pretty_print("ERROR: There was a problem with the connection.",
                                         TestrunnerUtils.TextDecorations.FAIL)
            receiving_output = False

    verbose_print("    Closing connection...")
    s.shutdown(socket.SHUT_RDWR)
    s.close()

    verbose_print("    Parsing Telnet output...")
    clean_telnet = TestrunnerUtils.clean_raw_telnet(telnet_output)

    # Get last result from telnet
    clean_telnet.reverse()
    test_start_idx = [i for i, item in enumerate(clean_telnet) if re.search('.*Running unit tests!.*', item)]
    if len(test_start_idx) > 0:
        last_result = clean_telnet[:test_start_idx[0]+1]
        last_result.reverse()
    else:
        TestrunnerUtils.pretty_print("ERROR: Cannot find any test results!",
                                     TestrunnerUtils.TextDecorations.FAIL)
        sys.exit(1)

    # Determine results of test suite
    try:
        result_chars = last_result[2]
    except IndexError as err:
        verbose_print("    Exception thrown: "+str(err))
        TestrunnerUtils.pretty_print("ERROR: Cannot find any test results!",
                                     TestrunnerUtils.TextDecorations.FAIL)
        sys.exit(1)

    num_of_tests = len(result_chars)
    num_of_fails = result_chars.count('F')
    num_of_errors = result_chars.count('E')
    num_of_passes = num_of_tests - (num_of_fails + num_of_errors)

    failure_dict = {}
    error_dict = {}

    test_suite_pass = False
    if num_of_passes == num_of_tests:
        test_suite_pass = True

    text_colour = TestrunnerUtils.TextDecorations.FAIL
    if test_suite_pass:
        text_colour = TestrunnerUtils.TextDecorations.OK_GREEN

    TestrunnerUtils.pretty_print("Tests ran: "+str(num_of_tests), TestrunnerUtils.TextDecorations.HEADER)
    TestrunnerUtils.pretty_print("    Tests passed: "+str(num_of_passes), text_colour)
    TestrunnerUtils.pretty_print("    Tests failed: "+str(num_of_fails), text_colour)
    TestrunnerUtils.pretty_print("    Test errors:  "+str(num_of_errors), text_colour)

    if test_suite_pass:
        TestrunnerUtils.pretty_print("All tests passed!", TestrunnerUtils.TextDecorations.HEADER)
    else:
        if num_of_fails > 0:
            TestrunnerUtils.pretty_print("Details of failures:", TestrunnerUtils.TextDecorations.HEADER)
            failures_idx = [i for i, item in enumerate(last_result) if re.search('FAIL:.*', item)]
            for failure_index in failures_idx:
                suite = path.basename(path.splitext(last_result[failure_index-1])[0])
                case = re.match('FAIL: (?P<name>\S*).*', last_result[failure_index]).group('name')
                message = last_result[failure_index+2]

                if suite not in failure_dict:
                    failure_dict[suite] = {}
                failure_dict[suite][case] = message

            for suite in failure_dict:
                print("    " + suite + ":")
                for case in failure_dict[suite]:
                    print("        " + case + ":")
                    print("            " + failure_dict[suite][case])

        if num_of_errors > 0:
            TestrunnerUtils.pretty_print("Details of errors:", TestrunnerUtils.TextDecorations.HEADER)
            errors_idx = [i for i, item in enumerate(last_result) if re.search('ERROR:.*', item)]
            for error_index in errors_idx:
                suite = path.basename(path.splitext(last_result[error_index-1])[0])
                case = re.match('ERROR: (?P<name>\S*).*', last_result[error_index]).group('name')
                message = last_result[error_index+2]

                if suite not in error_dict:
                    error_dict[suite] = {}
                error_dict[suite][case] = message

            for suite in error_dict:
                print("    " + suite + ":")
                for case in error_dict[suite]:
                    print("        " + case + ":")
                    print("            " + error_dict[suite][case])

    # Publish XML report
    TestrunnerUtils.pretty_print("Publishing XML report...", TestrunnerUtils.TextDecorations.HEADER)
    tree = TestrunnerUtils.create_junit_xml(num_of_tests, num_of_passes, num_of_fails, num_of_errors,
                                            failure_dict, error_dict)
    try:
        output_file = path.abspath(out_dir) + "\\" + out_name + ".xml"
        verbose_print("    Writing to " + output_file)
        tree.write(output_file, encoding="UTF-8", xml_declaration=True)
    except Exception as err:
        verbose_print("    Exception thrown: "+str(err))
        TestrunnerUtils.pretty_print("ERROR: Unable to write the test report XML file!",
                                     TestrunnerUtils.TextDecorations.FAIL)
        sys.exit(1)
    else:
        TestrunnerUtils.pretty_print("Testing complete!", TestrunnerUtils.TextDecorations.OK_BLUE)
        sys.exit(0)


def print_welcome():
    print("""
    ***********************
    ***  brstestrunner  ***
    ***********************
    """)

    verbose_print("Verbose Mode is ON\n", TestrunnerUtils.TextDecorations.WARNING)


def print_usage():
    print("""usage: """ + sys.argv[0] + """ --ip i [--outdir d] [--outname n] [--verbose]
    --ip i  IP address of the Roku device to test with
    --outdir d The directory to write the XML report to (Default is the current directory)
    --outname n The file name to use for the XML report (Default is 'report', produces report.xml)
    --verbose  Show more descriptive logging

    Example: """ + sys.argv[0] + """ --ip 192.168.1.78 --verbose""")


def verbose_print(string, colour="", decoration=""):
    if verbose_mode:
        TestrunnerUtils.pretty_print(string, colour, decoration)


if __name__ == "__main__":
    main(sys.argv[1:])
