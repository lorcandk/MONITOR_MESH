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

absolute_path = os.path.dirname(__file__)
devices_file = absolute_path + "/mesh_devices.txt"

with open(devices_file,'r') as file:
   extenders = []
   for line in file:
       line = line.strip()
       extenders.append(line)
file.close()
#print(extenders)

now = datetime.now() # current date and time
year = now.strftime("%Y")
month = now.strftime("%m")
day = now.strftime("%d")
time = now.strftime("%H:%M:%S")
date_time = now.strftime("%Y%m%d%H%M%S")

### Define file to save results ###
hostname = subprocess.check_output("hostname", shell=True, text=True)
result_file = absolute_path + "/monitor_mesh_" + hostname.strip() + "_" + date_time + ".csv"
print(f"Creating result file {result_file}")

#create symlink to new results file
sym_link = absolute_path + "/monitor_mesh_" + hostname.strip() + ".csv"
os.unlink(sym_link)
os.symlink(result_file,sym_link)
print(f"Creating sym link {sym_link} to {result_file}")

### Create headers in first row ###
headers = "Date,BSSID,ESSID,Freq,Signal,Latency,GW_IP,Google_IP,Google_FQDN_v4,Google_FQDN_v6"

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

### Check what subnet we are on ###
   my_ip_cmd = "hostname -I" 
   my_ip = subprocess.check_output(my_ip_cmd, shell=True, text=True)
   my_octets = my_ip.split('.')
   my_subnet = my_octets[0] + "." + my_octets[1] + "." + my_octets[2]
   print(f"My subnet is {my_subnet}") 

### Run NMAP to populate ARP table
   nmap_cmd = "/usr/bin/nmap -sP -n " + my_subnet + ".1-253"
   subprocess.run(nmap_cmd, shell=True, text=True)

### Get BSSID (Access Point MAC) and ESSID (WiFi network) ###
   bssid_cmd = "/sbin/iwgetid -a | /usr/bin/awk -F ': ' '{printf $2}'"
   essid_cmd = "/sbin/iwgetid | /usr/bin/awk -F ':' '{printf $2}'"
   signal_cmd = "/sbin/iwconfig wlan0 | grep 'Signal level' | /usr/bin/awk -F '=-' '{print $2}' | /usr/bin/awk -F ' dBm' '{print $1}'"
   freq_cmd = "/sbin/iwconfig wlan0 | grep 'Frequency' | /usr/bin/awk -F ' ' '{print $2}' | /usr/bin/awk -F ':' '{print $2}'"
   gw_wlan0_cmd = "ip route list dev wlan0 | /usr/bin/awk ' /^default/ {print $3}'"

   print("Getting wifi info...")
   bssid = subprocess.check_output(bssid_cmd, shell=True, text=True)
   essid = subprocess.check_output(essid_cmd, shell=True, text=True)
   signal = subprocess.check_output(signal_cmd, shell=True, text=True)
   freq = subprocess.check_output(freq_cmd, shell=True, text=True)
   gw_wlan0 = subprocess.check_output(gw_wlan0_cmd, shell=True, text=True)

### Ping Gateway and Google ###
   state_gw_ip_cmd = "ping -c 1 " + my_subnet + ".254 > /dev/null &&  echo 'up'  ||  echo 'down' "
   state_google_ip_cmd = "ping -c 1 8.8.8.8 > /dev/null &&  echo 'up'  ||  echo 'down' "
   state_google_fqdn_v4_cmd = "ping -4 -c 1 google.ie > /dev/null &&  echo 'up'  ||  echo 'down' "
   state_google_fqdn_v6_cmd = "ping -6 -c 1 google.ie > /dev/null &&  echo 'up'  ||  echo 'down' "
   latency_cmd = "ping -4 -c 1 www.google.com | grep -oP '.*time=\K\d+' "

   try:
      print(f"Running {state_gw_ip_cmd}")
      state_gw_ip = subprocess.check_output(state_gw_ip_cmd, shell=True, text=True)
   except:
      state_gw_ip = "down"
      print(f"GW ping check error")
   try:
      print(f"Running {state_google_ip_cmd}")
      state_google_ip = subprocess.check_output(state_google_ip_cmd, shell=True, text=True)
   except:
      state_google_ip = "down"
      print(f"Google IP ping check error")
   try:
      state_google_fqdn_v4 = subprocess.check_output(state_google_fqdn_v4_cmd, shell=True, text=True)
   except:
      state_google_fqdn_v4 = "down"
      print(f"Google FQDN ping check error")
   try:
      state_google_fqdn_v6 = subprocess.check_output(state_google_fqdn_v6_cmd, shell=True, text=True)
   except:
      state_google_fqdn_v6 = "down"
      print(f"Google FQDN IPv6 ping check error")
   try:
      latency = subprocess.check_output(latency_cmd, shell=True, text=True)
   except:
      latency = "-"
      print(f"Latency check error")

### Get time ###
   now = datetime.now()
   dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

### Create row of results ###
   results = dt_string.strip() + "," + bssid.strip() + "," + essid.strip() + "," + freq.strip() + "," + "-" + signal.strip() + "," + latency.strip() + "," + state_gw_ip.strip() + "," + state_google_ip.strip() + "," + state_google_fqdn_v4.strip() + "," + state_google_fqdn_v6.strip()

### Loop across extenders ###

   for i in extenders:
      mac_address = i

### Get IP address from ARP table ###
      cmd = "/usr/sbin/arp -n | grep -i " + mac_address + " | /usr/bin/awk -F ' ' '{printf $1}'"
      try:
         ip_address = subprocess.check_output(cmd, shell=True, text=True)
      except:
         print(f"ARP error for {mac_address}")
      print(f"IP address of {mac_address} is {ip_address}")

### Ping extender ###
      if is_valid_ipv4(ip_address):
         state_cmd = "ping -c 1 " + ip_address + " > /dev/null &&  echo 'up'  ||  echo 'down' "
         try:
            state = subprocess.check_output(state_cmd, shell=True, text=True)
         except:
            print(f"ping error for {ip_address}")
      else:
         print(f"Not valid IP address {ip_address}")
         state="down"

      results = results.strip() + "," + state.strip()

### Write results to file ###
   f.write(results)
   f.close()

