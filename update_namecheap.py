#!/usr/bin/env python3

import argparse
import time
import subprocess
import xml.etree.ElementTree as ET
import requests

# Example: ./update_namecheap.py --host www --domain example.com --password 15dbb231e1242342abbde42153fdaab1


def run_cmd(cmd_and_params):
    proc = subprocess.Popen(cmd_and_params, stdout=subprocess.PIPE)
    res, _ = proc.communicate()
    return res


def get_ip():
    ip = requests.get('https://api.ipify.org').content.decode('utf8')
    return ip


def tick(args, state):
    try:
        ip = get_ip()
        if ip != state["prev_ip"]:
            print("Detected new ip address: %s" % (ip,))
            for host in args.host:
                url = "https://dynamicdns.park-your-domain.com/update?host=%s" \
                    "&domain=%s&password=%s&ip=%s"
                cmd = url % (host, args.domain, args.password, ip)
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
                state["prev_ip"] = ip
                print("Succesfully updated %s.%s." % (host, args.domain))
    except ValueError:
        print("Failed. Trying again later.")
    

def main(state):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain',
                        help='Domain (e.g. example.com)', required=True)
    parser.add_argument('--host', nargs='+',
                        help='Host name (e.g. www)', required=True)
    parser.add_argument('-p', '--password',
                        help='Namecheap dynamic dns password', required=True)
    args = parser.parse_args()
    
    while True:
        tick(args, state)
        time.sleep(60)


if __name__ == "__main__":
    state = {"prev_ip": ""}
    main(state)
