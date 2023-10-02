import sys
import pandas as pd
import os
import subprocess
import socket
import re
from datetime import datetime

def is_valid_ipv4(ip):
    ipv4_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        octets = ip.split('.')
        for octet in octets:
            if not (0 <= int(octet) <= 255):
                return False
        return True
    return False

### Get Extender MAC addresses from file
extenders_df = pd.read_csv('~/MONITOR_MESH/mesh_devices.csv')

hostname = subprocess.check_output("hostname", shell=True, text=True)
result_file = "monitor_mesh_" + hostname.strip() + ".csv"

headers = "Date,BSSID,ESSID,GW_IP,Google_IP,Google_FQDN_v4,Google_FQDN_v6"
print(f"Initial Headers: {headers}")

for ind in extenders_df.index:
   name = extenders_df['Name'][ind]
   headers = headers + "," + name 

print(f"All Headers {headers}")

f = open(result_file, 'a+')
f.write("\n")
f.write(headers)
#f.close()

while True:

### Run NMAP to populate ARP table
   os.system("/usr/bin/nmap -sP -n 192.168.1.1-253")

### Get BSSID (Access Point MAC) and ESSID (WiFi network) ###
   bssid_cmd = "/sbin/iwgetid -a | /usr/bin/awk -F ': ' '{printf $2}'"
   essid_cmd = "/sbin/iwgetid | /usr/bin/awk -F ':' '{printf $2}'"
   gw_wlan0_cmd = "ip route list dev wlan0 | awk ' /^default/ {print $3}'"

   bssid = subprocess.check_output(bssid_cmd, shell=True, text=True)
   essid = subprocess.check_output(essid_cmd, shell=True, text=True)
   gw_wlan0 = subprocess.check_output(gw_wlan0_cmd, shell=True, text=True)

   print(f"ESSID: {essid} BSSID: {bssid} Gateway: {gw_wlan0}")

### Ping Gateway and Google ###
   state_gw_ip_cmd = "ping -c 1 192.168.1.254 > /dev/null &&  echo 'up'  ||  echo 'down' "
   state_google_ip_cmd = "ping -c 1 8.8.8.8 > /dev/null &&  echo 'up'  ||  echo 'down' "
   state_google_fqdn_v4_cmd = "ping -4 -c 1 google.ie > /dev/null &&  echo 'up'  ||  echo 'down' "
   state_google_fqdn_v6_cmd = "ping -6 -c 1 google.ie > /dev/null &&  echo 'up'  ||  echo 'down' "

   state_gw_ip = subprocess.check_output(state_gw_ip_cmd, shell=True, text=True)
   state_google_ip = subprocess.check_output(state_google_ip_cmd, shell=True, text=True)
   state_google_fqdn_v4 = subprocess.check_output(state_google_fqdn_v4_cmd, shell=True, text=True)
   state_google_fqdn_v6 = subprocess.check_output(state_google_fqdn_v6_cmd, shell=True, text=True)

   now = datetime.now()
   dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

   results = dt_string.strip() + "," + bssid.strip() + "," + essid.strip() + "," + state_gw_ip.strip() + "," + state_google_ip.strip() + "," + state_google_fqdn_v4.strip() + "," + state_google_fqdn_v6.strip() 
   print(f"Initial Results: {results}")

### Loop extenders
   for ind in extenders_df.index:

      name = extenders_df['Name'][ind]
      mac_address = extenders_df['MAC'][ind]

      cmd = "/usr/sbin/arp -n | grep -i " + mac_address + " | /usr/bin/awk -F ' ' '{printf $1}'" 

      ip_address = subprocess.check_output(cmd, shell=True, text=True)

      if is_valid_ipv4(ip_address):
         state_cmd = "ping -c 1 " + ip_address + " > /dev/null &&  echo 'up'  ||  echo 'down' "
         state = subprocess.check_output(state_cmd, shell=True, text=True)
      else:
         state="NA"

      results = results.strip() + "," + state.strip()

      print(f"Name: {name} MAC: {mac_address} IP: {ip_address} State: {state}")

      print(f"Ext Results: {results}")

   print(f"All Results: {results}")

#   f = open("monitor_mesh_test.txt", "a")
   f.write("\n")
   f.write(results)

#   input("Press Enter to continue...")

f.close()
