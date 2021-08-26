#!/usr/bin/python

#   Copyright 2021 Chandler Willoughby
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
import csv



def getProcessId(name):
    proc = subprocess.Popen(['pidof', name], stdout=subprocess.PIPE)
    stdout_value = proc.communicate()[0].decode("utf-8")
    return stdout_value

def getNtpdStats():
    data = dict()
    proc = subprocess.Popen(['ntpq', '-p'], stdout=subprocess.PIPE)
    stdout_value = proc.communicate()[0].decode("utf-8")
    start = stdout_value.find("===\n")
    peerList = stdout_value[start+4:]
    ntpdPeerRegex = "(?P<status>.)(?P<remote>\S+)\s+(?P<refid>\S+)\s+(?P<st>\S+)\s+(?P<t>\S+)\s+(?P<when>\S+)\s+(?P<poll>\S+)\s+(?P<reach>\S+)\s+(?P<delay>\S+)\s+(?P<offset>\S+)\s+(?P<jitter>\S+)\s+"
    pattern = re.compile(ntpdPeerRegex, re.MULTILINE)
    peers = pattern.findall(peerList)
    for peer in peers:
        peerData = {
            "timeDaemon":"ntpd",
            "dataType":"sources",
            "status":peer[0],
            "remote":peer[1],
            "refid":peer[2],
            "st":int(peer[3]),
            "t":peer[4],
            "when":peer[5],
            "poll":int(peer[6]),
            "reach":int(peer[7]),
            "delay":float(peer[8]),
            "offset":float(peer[9]),
            "jitter":float(peer[10])
            }
        print(json.dumps({"ntpqt_data":peerData}))
    return

def getChronydStats():
    sourcesData = dict()
    trackingData = dict()
    def getChronydSources():
        data = dict()
        proc = subprocess.Popen(['chronyc', '-c', 'sources'], stdout=subprocess.PIPE)
        stdout_value = proc.communicate()[0].decode("utf-8")
        csvReader = csv.reader(stdout_value.splitlines(), delimiter=',')
        for source in csvReader:
            sourceData = dict()
            sourceData = {
                "timeDaemon":"chronyd",
                "dataType":"sources",
                "mode": source[0],
                "state": source[1],
                "name": source[2],
                "stratum": source[3],
                "poll": source[4],
                "reach": source[5],
                "lastrx": source[6],
                "offset": source[7],
                "actualoffset": source[8],
                "lastsample": source[9]
            }
            print(json.dumps({"ntpqt_data":sourceData}))
    def getChronydTracking():
        data = dict()
        proc = subprocess.Popen(['chronyc', '-c', 'tracking'], stdout=subprocess.PIPE)
        stdout_value = proc.communicate()[0].decode("utf-8")
        csvReader = csv.reader(stdout_value.splitlines(), delimiter=',')
        for tracking in csvReader:
            trackingData = dict()
            trackingData = {
                "timeDaemon":"chronyd",
                "dataType":"tracking",
                "referenceid":tracking[0],
                "name":tracking[1],
                "stratum":tracking[2],
                "reftime":tracking[3],
                "systemtime":tracking[4],
                "lastoffset":tracking[5],
                "rmsoffset":tracking[6],
                "frequency":tracking[7],
                "residualfrequency":tracking[8],
                "skew":tracking[9],
                "rootdelay":tracking[10],
                "rootdispersion":tracking[11],
                "updateinterval":tracking[12],
                "leapstatus":tracking[13]
            }
            print(json.dumps({"ntpqt_data":trackingData}))
    getChronydSources()
    getChronydTracking()

pidOfNtpd = getProcessId("ntpd")
pidOfChronyd = getProcessId("chronyd")

if pidOfChronyd and pidOfNtpd:
    print("This host appears to be running multiple time sync daemons, this could be problematic.")
elif pidOfNtpd:
    getNtpdStats()
elif pidOfChronyd:
    print("This host is running Chronyd! Gathering stats from the Chrony daemon.")
    getChronydStats()
else:
    print("This host doesn't seem to be running any time syncronization daemon, this could be problematic.")
