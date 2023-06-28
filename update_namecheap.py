#!/usr/bin/env python3

import time
import subprocess
import xml.etree.ElementTree as ET
import sys

HOSTNAMES=["www"]
DOMAIN="mydomain.com"
PASSWORD="mynamecheapdynamicupdatepassword"

def run_cmd(cmd_and_params):
    proc = subprocess.Popen(cmd_and_params, stdout=subprocess.PIPE)
    res, _ = proc.communicate()
    return res

prev_ip = None
while True:
    try:
        ip = run_cmd(["curl", "-s", "ipecho.net/plain"])
        ip = ip.split(b'.')
        if len(ip) != 4:
            raise ValueError("Wrong num of parts")
        for part in ip:
            _ = int(part)
        ip = b'.'.join(ip).decode("utf8")
        if ip != prev_ip:
            print("Detected new ip address: %s" % (ip,))
            for host in HOSTNAMES:
                cmd = "https://dynamicdns.park-your-domain.com/update?host=%s&domain=%s&password=%s&ip=%s" % (host, DOMAIN, PASSWORD, ip)
                res = run_cmd(["curl", "-s", cmd])
                if not res:
                    raise ValueError("No valid response")
                res = res.decode("utf8", errors="ignore")
                root = ET.fromstring(res)
                ok = False
                for errs in root.findall("ErrCount"):
                    num_errs = int(errs.text)
                    if num_errs == 0:
                        ok = True
                if not ok:
                    print(res)
                    raise ValueError("Error response")
                prev_ip = ip
                print("Succesfully updated %s.%s." % (host, DOMAIN))
    except ValueError:
        print("Failed. Trying again later.")
    time.sleep(30)
