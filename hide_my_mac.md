# Usage
### Command line
```bash
python3 hide_my_mac.py --ip {{your_ip}}  --gateway_ip {{gateway_ip}} --iface eth0
```

### Explanation
```text
--ip: Your IP address
--gateway_ip: Gateway IP address
--iface: Your network interface
```
It's possible to get your IP address from your iface, but I am too lazy to do that

# Requirement
## Disable kernel ARP Response
Since the ARP response is enabled by default, we have to disable it for such interface.
```bash
echo 2 > /proc/sys/net/ipv4/conf/eth0/arp_ignore
echo 1 > /proc/sys/net/ipv4/conf/eth0/arp_announce
```
Or disable all
```bash
echo 2 > /proc/sys/net/ipv4/conf/all/arp_ignore
echo 1 > /proc/sys/net/ipv4/conf/all/arp_announce
```

In case you want to restore to the default, here is the default values of these 2 configs
```bash
echo 0 > /proc/sys/net/ipv4/conf/all/arp_ignore
echo 0 > /proc/sys/net/ipv4/conf/all/arp_announce
```

# Privileges
Since this script requires some privileges, you have two choices
1. Run as root
2. Run with CAP_NET_RAW enabled
```bash
sudo setcap cap_net_raw=eip $(which python3) 
```
With (2) you better create a virtualenv and install scapy, and run with that venv

3. Run with Docker
```bash
docker build -t hide-my-mac -f hide_my_mac.Dockerfile
docker run --rm --cap-add=NET_RAW --cap-add=NET_ADMIN --network host -v /sys/class/net:/sys/class/net  -e PYTHONUNBUFFERED=1 hide-my-mac --ip {{your_ip}}  --gateway_ip {{gateway_ip}} --iface eth0 
```
