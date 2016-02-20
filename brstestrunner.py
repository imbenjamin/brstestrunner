#!/usr/bin/python

from utils import TestrunnerUtils, RokuUtils

import sys
import getopt
import ipaddress
import time
import socket
import re

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
    test_pass = ["...........................................................................................................................................................................................................\r\n----------------------------------------------------------------------\r\nRan 1228 tests\r\n\r\nOK\r\n\r\n###################################################\r\n                Test suite complete                \r\n###################################################\r\nNote: GC - Found 936 orphaned objects (objects in a circular ref loop).\r\n\r\n------ Running dev 'NOW TV' main ------\r\n###################################################\r\n                Running unit tests!                \r\n###################################################\r\n............................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................\r\n----------------------------------------------------------------------\r\nRan 1228 tests\r\n\r\nOK\r\n\r\n###################################################\r\n                Test suite complete                \r\n###################################################\r\nNote: GC - Found 936 orphaned objects (objects in a circular ref loop).\r\n\r\n------ Running dev 'NOW TV' main ------\r\n###################################################\r\n                Running unit tests!                \r\n###################################################\r\n............................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................\r\n----------------------------------------------------------------------\r\nRan 1228 tests\r\n\r\nOK\r\n\r\n###################################################\r\n                Test suite complete                \r\n###################################################\r\nNote: GC - Found 936 orphaned objects (objects in a circular ref loop).\r\n\r\n------ Running dev 'NOW TV' main ------\r\n", '###################################################\r\n', '                Running unit tests!                \r\n###################################################\r\n', '......................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................', '......................................................................................................................................................................................................................................................................................................................................................................................\r\n----------------------------------------------------------------------\r\nRan 1228 tests\r\n\r\nOK\r\n\r\n###################################################\r\n                Test suite complete                \r\n###################################################\r\n', 'Note: GC - Found 936 orphaned objects (objects in a circular ref loop).\r\n']
    test_fail = ["----\r\nRan 1228 tests\r\n\r\nOK\r\n\r\n###################################################\r\n                Test suite complete                \r\n###################################################\r\nNote: GC - Found 936 orphaned objects (objects in a circular ref loop).\r\n\r\n------ Running dev 'NOW TV' main ------\r\n###################################################\r\n                Running unit tests!                \r\n###################################################\r\n............................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................\r\n----------------------------------------------------------------------\r\nRan 1228 tests\r\n\r\nOK\r\n\r\n###################################################\r\n                Test suite complete                ", "\r\n###################################################\r\nNote: GC - Found 936 orphaned objects (objects in a circular ref loop).\r\n\r\n------ Running dev 'NOW TV' main ------\r\n###################################################\r\n                Running unit tests!                \r\n###################################################\r\nF............................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................\r\n======================================================================\r\npkg:/source/data/testAbstractContentData.brs\r\nFAIL: testAssertFalseIsTrue\r\n----------------------------------------------------------------------\r\nexpression evaluates to false\r\n\r\n----------------------------------------------------------------------\r\nRan 1229 tests\r\n\r\nFAILED (failures= 1)\r\n\r\n###################################################\r\n                Test suite complete                \r\n###################################################\r\nNote: GC - Found 936 orphaned objects (objects in a circular ref loop).\r\n\r\n------ Running dev 'NOW TV' main ------\r\n", '###################################################\r\n', '                Running unit tests!                \r\n###################################################\r\n', 'F............................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................\r\n', '======================================================================\r\npkg:/source/data/testAbstractContentData.brs\r\nFAIL: testAssertFalseIsTrue\r\n----------------------------------------------------------------------\r\nexpression evaluates to false\r\n\r\n----------------------------------------------------------------------\r\nRan 1229 tests\r\n\r\nFAILED (failures= 1)\r\n\r\n###################################################\r\n                Test suite complete                \r\n###################################################\r\n', 'Note: GC - Found 936 orphaned objects (objects in a circular ref loop).\r\n']
    test_multifail_error = ['.........................................................................', "...................................................................................................................................................................................................................................\r\n======================================================================\r\npkg:/source/data/testAbstractContentData.brs\r\nERROR: testDeliberateError\r\n----------------------------------------------------------------------\r\nMember function not found in BrightScript Component or interface (ERR_RO2)\r\n\r\n======================================================================\r\npkg:/source/data/testAbstractContentData.brs\r\nFAIL: testAssertFalseIsTrue\r\n----------------------------------------------------------------------\r\nexpression evaluates to false\r\n\r\n======================================================================\r\npkg:/source/data/testAbstractContentData.brs\r\nFAIL: testAssertFalseIsTrue2\r\n----------------------------------------------------------------------\r\nexpression evaluates to false\r\n\r\n----------------------------------------------------------------------\r\nRan 1231 tests\r\n\r\nFAILED (failures= 2, errors= 1)\r\n\r\n###################################################\r\n                Test suite complete                \r\n###################################################\r\nNote: GC - Found 936 orphaned objects (objects in a circular ref loop).\r\n\r\n------ Running dev 'NOW TV' main ------\r\n##############################", '#####################\r\n                Running unit tests!                \r\n###################################################\r\nFFE............................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................\r\n======================================================================\r\npkg:/source/data/testAbstr', "actContentData.brs\r\nERROR: testDeliberateError\r\n----------------------------------------------------------------------\r\nMember function not found in BrightScript Component or interface (ERR_RO2)\r\n\r\n======================================================================\r\npkg:/source/data/testAbstractContentData.brs\r\nFAIL: testAssertFalseIsTrue\r\n----------------------------------------------------------------------\r\nexpression evaluates to false\r\n\r\n======================================================================\r\npkg:/source/data/testAbstractContentData.brs\r\nFAIL: testAssertFalseIsTrue2\r\n----------------------------------------------------------------------\r\nexpression evaluates to false\r\n\r\n----------------------------------------------------------------------\r\nRan 1231 tests\r\n\r\nFAILED (failures= 2, errors= 1)\r\n\r\n###################################################\r\n                Test suite complete                \r\n###################################################\r\nNote: GC - Found 936 orphaned objects (objects in a circular ref loop).\r\n\r\n------ Running dev 'NOW TV' main ------\r\n", '###################################################\r\n', '                Running unit tests!                \r\n###################################################\r\n', 'FFE............................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................\r\n', '======================================================================\r\npkg:/source/data/testAbstractContentData.brs\r\nERROR: testDeliberateError\r\n----------------------------------------------------------------------\r\nMember function not found in BrightScript Component or interface (ERR_RO2)\r\n\r\n======================================================================\r\npkg:/source/data/testAbstractContentData.brs\r\nFAIL: testAssertFalseIsTrue\r\n----------------------------------------------------------------------\r\nexpression evaluates to false\r\n\r\n======================================================================\r\npkg:/source/data/testAbstractContentData.brs\r\nFAIL: testAssertFalseIsTrue2\r\n----------------------------------------------------------------------\r\nexpression evaluates to false\r\n\r\n----------------------------------------------------------------------\r\nRan 1231 tests\r\n\r\nFAILED (failures= 2, errors= 1)\r\n\r\n###################################################\r\n                Test suite complete                \r\n###################################################\r\n', 'Note: GC - Found 936 orphaned objects (objects in a circular ref loop).\r\n']

    # telnet_output = test_pass
    telnet_output = test_multifail_error

    # telnet_output = []
    # while job_running:
    #     try:
    #         # Receive data from the socket
    #         data = s.recv(4096)
    #         if not data:
    #             # Host has terminated the connection
    #             TestrunnerUtils.pretty_print("ERROR: The connection was prematurely terminated by the host.",
    #                                          TestrunnerUtils.TextDecorations.FAIL)
    #             sys.exit(1)
    #         else:
    #             # Store the line
    #             telnet_output.append(data.decode())
    #     except socket.timeout:
    #         # Socket has timed out, no more Telnet output is being received
    #         verbose_print("    No more Telnet output to read.")
    #         job_running = False
    #     except ConnectionError as err:
    #         # Some other ConnectionError has occurred
    #         verbose_print("    Exception thrown: "+err.strerror)
    #         TestrunnerUtils.pretty_print("ERROR: There was a problem with the connection.",
    #                                      TestrunnerUtils.TextDecorations.FAIL)
    #         job_running = False

    verbose_print("    Closing connection...")
    s.shutdown(socket.SHUT_RDWR)
    s.close()

    # print(telnet_output)

    verbose_print("    Parsing Telnet output...")
    clean_telnet = TestrunnerUtils.clean_raw_telnet(telnet_output)

    # Get last result from telnet
    clean_telnet.reverse()
    test_start_idx = [i for i, item in enumerate(clean_telnet) if re.search('.*Running unit tests!.*', item)]
    if len(test_start_idx) > 0:
        last_result = clean_telnet[:test_start_idx[0]+1]
        last_result.reverse()
        print(last_result)
    else:
        TestrunnerUtils.pretty_print("ERROR: Cannot find any test results!",
                                     TestrunnerUtils.TextDecorations.FAIL)
        sys.exit(1)

    # Determine results of test suite
    result_chars = last_result[2]

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
                file = last_result[failure_index-1]
                function_name = re.match('FAIL: (?P<name>\S*).*', last_result[failure_index]).group('name')
                reason = last_result[failure_index+2]

                if file not in failure_dict:
                    failure_dict[file] = {}
                failure_dict[file][function_name] = reason

            for file in failure_dict:
                print("    " + file + ":")
                for function_name in failure_dict[file]:
                    print("        " + function_name + ":")
                    print("            " + failure_dict[file][function_name])

        if num_of_errors > 0:
            TestrunnerUtils.pretty_print("Details of errors:", TestrunnerUtils.TextDecorations.HEADER)
            errors_idx = [i for i, item in enumerate(last_result) if re.search('ERROR:.*', item)]
            for error_index in errors_idx:
                file = last_result[error_index-1]
                function_name = re.match('ERROR: (?P<name>\S*).*', last_result[error_index]).group('name')
                reason = last_result[error_index+2]

                if file not in error_dict:
                    error_dict[file] = {}
                error_dict[file][function_name] = reason

            for file in error_dict:
                print("    " + file + ":")
                for function_name in error_dict[file]:
                    print("        " + function_name + ":")
                    print("            " + error_dict[file][function_name])


def print_welcome():
    print("""
    ***********************
    ***  brstestrunner  ***
    ***********************
    """)

    verbose_print("Verbose Mode is ON\n", TestrunnerUtils.TextDecorations.WARNING)


def print_usage():
    print("""usage: " + sys.argv[0] + " --ip i [--verbose]
    --ip i  IP address of the Roku device to test with
    --verbose  Show more descriptive logging

    Example: " + sys.argv[0] + " --ip 192.168.1.78 --verbose""")


def verbose_print(string, colour="", decoration=""):
    if verbose_mode:
        TestrunnerUtils.pretty_print(string, colour, decoration)


if __name__ == "__main__":
    main(sys.argv[1:])
