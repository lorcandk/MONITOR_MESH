import sys
import os
import subprocess
import socket
import re
from datetime import datetime

### function to check validity of IP address ###
def is_valid_ipv4(ip):
    ipv4_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        octets = ip.split('.')
        for octet in octets:
            if not (0 <= int(octet) <= 255):
                return False
        return True
    return False

### Get Extender MAC addresses from file ###
#extenders_df = pd.read_csv('~/MONITOR_MESH/mesh_devices.csv')

with open('mesh_devices.txt','r') as file:
   extenders = []
   for line in file:
       line = line.strip()
       extenders.append(line)
file.close()
#print(extenders)

### Define file to save results ###
hostname = subprocess.check_output("hostname", shell=True, text=True)
result_file = "monitor_mesh_" + hostname.strip() + ".csv"
print(result_file)

### Create headers in first row ###
headers = "Date,BSSID,ESSID,GW_IP,Google_IP,Google_FQDN_v4,Google_FQDN_v6"

#for ind in extenders_df.index:
#   name = extenders_df['Name'][ind]
#   headers = headers + "," + name 

for i in extenders:
   ext_name = "Ext_" + i[-5:]
   ext_name = ext_name.replace(":", "")
   headers = headers + "," + ext_name 

#print(headers)

### Open result file for appending ###
f = open(result_file, 'a+')
f.write("\n")
f.write(headers)
f.close()

### Loop continuously ###
while True:
 
### Open result file for appending ###
   f = open(result_file, 'a+')
   f.write("\n")

### Run NMAP to populate ARP table
   os.system("/usr/bin/nmap -sP -n 192.168.1.1-253")

### Get BSSID (Access Point MAC) and ESSID (WiFi network) ###
   bssid_cmd = "/sbin/iwgetid -a | /usr/bin/awk -F ': ' '{printf $2}'"
   essid_cmd = "/sbin/iwgetid | /usr/bin/awk -F ':' '{printf $2}'"
   gw_wlan0_cmd = "ip route list dev wlan0 | awk ' /^default/ {print $3}'"

   bssid = subprocess.check_output(bssid_cmd, shell=True, text=True)
   essid = subprocess.check_output(essid_cmd, shell=True, text=True)
   gw_wlan0 = subprocess.check_output(gw_wlan0_cmd, shell=True, text=True)

### Ping Gateway and Google ###
   state_gw_ip_cmd = "ping -c 1 192.168.1.254 > /dev/null &&  echo 'up'  ||  echo 'down' "
   state_google_ip_cmd = "ping -c 1 8.8.8.8 > /dev/null &&  echo 'up'  ||  echo 'down' "
   state_google_fqdn_v4_cmd = "ping -4 -c 1 google.ie > /dev/null &&  echo 'up'  ||  echo 'down' "
   state_google_fqdn_v6_cmd = "ping -6 -c 1 google.ie > /dev/null &&  echo 'up'  ||  echo 'down' "

   state_gw_ip = subprocess.check_output(state_gw_ip_cmd, shell=True, text=True)
   state_google_ip = subprocess.check_output(state_google_ip_cmd, shell=True, text=True)
   state_google_fqdn_v4 = subprocess.check_output(state_google_fqdn_v4_cmd, shell=True, text=True)
   state_google_fqdn_v6 = subprocess.check_output(state_google_fqdn_v6_cmd, shell=True, text=True)

### Get time ###
   now = datetime.now()
   dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

### Create row of results ###
   results = dt_string.strip() + "," + bssid.strip() + "," + essid.strip() + "," + state_gw_ip.strip() + "," + state_google_ip.strip() + "," + state_google_fqdn_v4.strip() + "," + state_google_fqdn_v6.strip() 

### Loop across extenders ###
#   for ind in extenders_df.index:

#     name = extenders_df['Name'][ind]
#     mac_address = extenders_df['MAC'][ind]

   for i in extenders:
      mac_address = i

### Get IP address from ARP table ###
      cmd = "/usr/sbin/arp -n | grep -i " + mac_address + " | /usr/bin/awk -F ' ' '{printf $1}'" 
      ip_address = subprocess.check_output(cmd, shell=True, text=True)

### Ping extender ###
      if is_valid_ipv4(ip_address):
         state_cmd = "ping -c 1 " + ip_address + " > /dev/null &&  echo 'up'  ||  echo 'down' "
         state = subprocess.check_output(state_cmd, shell=True, text=True)
      else:
         state="NA"

      results = results.strip() + "," + state.strip()

### Write results to file ###
   f.write(results)
   f.close()
