Script to monitor Mesh WiFi extenders

Run the script on a probe that is wifi connected to an extender

Script repeatedly pings all extenders plus the gateway and Internet
Output includes up/down status, connected SSID and signal/channel

Setup:
Add MAC addresses of the extenders to mesh_devices.txt

Usage:
   python3 monitor_mesh.py

Output:
Saved to file monitor_mesh_<hostname>.csv

Monitor output in real time using tail

   tail -F monitor_mesh_<hostname>.csv

Recommendations:

Run script inside a tmux session.

start tmux session: tmux
detach from tmux session: CTRL-D B
reattach to tmux session: tmux a

