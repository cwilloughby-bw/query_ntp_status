#!/usr/bin/python

#   Copyright 2018 Kevin Godden
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import subprocess
import json
import re
import sys

# Shell out to 'ntpq -p'
proc = subprocess.Popen(['/usr/sbin/ntpq', '-p'], stdout=subprocess.PIPE)

# Get the output
stdout_value = proc.communicate()[0].decode("utf-8")

#remove the header lines
start = stdout_value.find("===\n")

if start == -1:
    # We may be running on windows (\r\n), try \r...
    start = stdout_value.find("===\r")

    if start == -1:
        # No, go, exit with error
        result = {'query_result': 'failed', 'data': {}}
        print(json.dumps(result))
        sys.exit(1)

# Get the data part of the string
pay_dirt = stdout_value[start+4:]

expression = "(?P<status>.)(?P<remote>\S+)\s+(?P<refid>\S+)\s+(?P<st>\S+)\s+(?P<t>\S+)\s+(?P<when>\S+)\s+(?P<poll>\S+)\s+(?P<reach>\S+)\s+(?P<delay>\S+)\s+(?P<offset>\S+)\s+(?P<jitter>\S+)\s+"

pattern = re.compile(expression, re.MULTILINE)
r = pattern.findall(pay_dirt)

data = dict()

for match in r:
    serverdata = {
        "status":match[0],
        "refid":match[2],
        "st":match[3],
        "t":match[4],
        "when":match[5],
        "poll":match[6],
        "reach":match[7],
        "delay":match[8],
        "offset":match[9],
        "jitter":match[10]
        }
    data[match[1]] = serverdata

# Output Result
result = {'query_result': 'ok' if r else 'failed', 'data': data}

print(json.dumps(result))
