# brstestrunner
A test runner for automatically running a Roku unit test package using
[brstest](https://github.com/MarkRoddy/brstest), and outputting a JUnit-compatible test report.

### Prerequisites
* Python 2.6 or above (written for 2.6.8)
* The brstest package must be installed on the target Roku device before running the script.
* At present the script looks for the string "Running unit tests!" to mark the beginning of a brstest session. You will
need to add `print "Running unit tests!"` before you call `BrsTestMain()` in your BrightScript test app. Surrounding
text is allowed. Eg: `print "*** Running unit tests! ***"`. Extra print statements after running `BrsTestMain()` is
allowed.

### Usage
`python brstestrunner.py --ip <device ip> [--output <output file>] [-v] [-h]`

`-v = Verbose Mode` `-h = Help/Show usage`

The test runner utilises a Telnet connection to the target Roku device. As only one Telnet connection at a time is
allowed on a Roku device, you must remember to disconnect any existing Telnet connection (such as a debugger session)
before running the test runner.

### What does the script actually do?
1. Checks that the IP address given as a valid IP address
2. Checks that a dev channel app is installed on the target Roku device
3. Launches the dev channel app (the brstest app)
4. Opens a Telnet connection to the target Roku device and reads output until nothing more is being output
5. Parses the Telnet output, only paying attention to the most recent testing session (a Telnet session can span
multiple app lifetimes)
6. Produces an XML report in JUnit-style, compatible with CI environments such as Jenkins.

### License
Copyright (c) 2016 Benjamin Hill

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
