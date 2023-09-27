### Script to monitor Mesh WiFi Extenders ###

filename="$HOME/monitor_mesh_$(hostname).csv"

echo "Monitor script started at $(date)" >> $filename

echo "Date,BSSID,ESSID,GW_IP,Google_IP,Google_FQDN_v4,Google_FQDN_v6,Ext_B840,Ext_8440,Ext_B840,Ext_B878" >> $filename

while :; do

### Run NMAP to populate ARP table ###

/usr/bin/nmap -sP -n 192.168.1.1-253

### Get BSSID (Access Point MAC) and ESSID (WiFi network) ###

bssid=$(/sbin/iwgetid -a | /usr/bin/awk -F ': ' '{printf $2}')
essid=$(/sbin/iwgetid | /usr/bin/awk -F ':' '{printf $2}')

### Get Default Gateway ###

gw_wlan0=$(ip route list dev wlan0 | awk ' /^default/ {print $3}')

### Get the IP addresses of the extenders ###

#ip_88C0=$(/usr/sbin/arp -n | grep -i 08:d5:9d:fb:88:c0 | /usr/bin/awk -F ' ' '{printf $1}')
#ip_B840=$(/usr/sbin/arp -n | grep -i 20:9a:7d:fa:b8:40 | /usr/bin/awk -F ' ' '{printf $1}')
#ip_8740=$(/usr/sbin/arp -n | grep -i 08:d5:9d:fb:87:40 | /usr/bin/awk -F ' ' '{printf $1}')
#ip_B878=$(/usr/sbin/arp -n | grep -i 20:9a:7d:fa:b8:78 | /usr/bin/awk -F ' ' '{printf $1}')
#ip_8508=$(/usr/sbin/arp -n | grep -i 08:D5:9D:FB:85:08 | /usr/bin/awk -F ' ' '{printf $1}')
#ip_88D8=$(/usr/sbin/arp -n | grep -i 08:d5:9d:fb:88:d8 | /usr/bin/awk -F ' ' '{printf $1}')
#ip_8430=$(/usr/sbin/arp -n | grep -i 08:d5:9d:fb:84:30 | /usr/bin/awk -F ' ' '{printf $1}')
#ip_8750=$(/usr/sbin/arp -n | grep -i 08:d5:9d:fb:87:50 | /usr/bin/awk -F ' ' '{printf $1}')

ip_8430=$(/usr/sbin/arp -n | grep -i 08:d5:9d:fb:84:30 | /usr/bin/awk -F ' ' '{printf $1}')
ip_8440=$(/usr/sbin/arp -n | grep -i 80:d5:9d:fb:84:40 | /usr/bin/awk -F ' ' '{printf $1}')
ip_B840=$(/usr/sbin/arp -n | grep -i 20:9a:7d:fa:b8:40 | /usr/bin/awk -F ' ' '{printf $1}')
ip_B878=$(/usr/sbin/arp -n | grep -i 20:9a:7d:fa:b8:78 | /usr/bin/awk -F ' ' '{printf $1}')

### Ping Gateway and Google ###

state_gw_ip=$(ping -c 1 192.168.1.254 > /dev/null &&  echo "up"  ||  echo "down" )
state_google_ip=$(ping -c 1 8.8.8.8 > /dev/null &&  echo "up"  ||  echo "down" )
state_google_fqdn_v4=$(ping -4 -c 1 google.ie > /dev/null &&  echo "up"  ||  echo "down" )
state_google_fqdn_v6=$(ping -6 -c 1 google.ie > /dev/null &&  echo "up"  ||  echo "down" )

#state_gw_router=$(ping -c 1 $gw_wlan0 > /dev/null &&  echo "up"  ||  echo "down" )

### Ping Extender 1 ###

if [[ $ip_8430 =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        state_ext_8430=$(ping -c 1 $ip_8430 > /dev/null &&  echo "up"  ||  echo "down" )
else
        state_ext_8430="NA"
fi


### Ping Extender 2 ###

if [[ $ip_8440 =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        state_ext_8440=$(ping -c 1 $ip_8440 > /dev/null &&  echo "up"  ||  echo "down" )
else
        state_ext_8440="NA"
fi


### Ping Extender 3 ###

if [[ $ip_B840 =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        state_ext_B840=$(ping -c 1 $ip_B840 > /dev/null &&  echo "up"  ||  echo "down" )
else
        state_ext_B840="NA"
fi

### Ping Extender 4 ###

if [[ $ip_B878 =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        state_ext_B878=$(ping -c 1 $ip_B878 > /dev/null &&  echo "up"  ||  echo "down" )
else
        state_ext_B878="NA"
fi


echo "$(date),$bssid,$essid,\
$state_gw_ip,\
$state_google_ip,$state_google_fqdn_v4,$state_google_fqdn_v6,\
$state_ext_8430,$state_ext_8440,$state_ext_B840,\
$state_ext_B878" >> $filename

sleep 10
done

