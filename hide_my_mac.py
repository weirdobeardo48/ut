import random
import string
import click
from scapy.all import ARP, Ether, srp, sniff, sendp, get_if_hwaddr


def generate_random_mac():
    return '00:11:22:' + ':'.join([''.join(random.choices(string.hexdigits[:16], k=2)) for _ in range(3)])


def get_gateway_mac(gateway_ip, iface):
    arp_request = ARP(pdst=gateway_ip)
    ether_frame = Ether(dst="ff:ff:ff:ff:ff:ff") / arp_request

    response = srp(ether_frame, timeout=2, iface=iface, verbose=False)[0]

    for _, pkt in response:
        if pkt.haslayer(ARP):
            return pkt[ARP].hwsrc
    return None


def handle_arp_request(pkt, my_ip, gateway_ip, gateway_mac, fake_mac, iface, my_mac):
    if pkt.haslayer(ARP) and pkt[ARP].op == 1:
        requested_ip = pkt[ARP].pdst

        if requested_ip == my_ip:
            source_ip = pkt[ARP].psrc

            count = 1
            if source_ip == gateway_ip:
                print(f"ARP request for {requested_ip} from gateway {source_ip}. Responding with my MAC {my_mac}.")
                arp_response = ARP(op=2, psrc=my_ip, hwsrc=my_mac, pdst=requested_ip)
                eth = Ether(dst=gateway_mac)
            else:
                count = 10
                print(
                    f"ARP request for {requested_ip} from {source_ip}. Responding with fake MAC {fake_mac} to {pkt[Ether].src}.")
                arp_response = ARP(op=2, psrc=my_ip, hwsrc=fake_mac, pdst=requested_ip)
                eth = Ether(src=fake_mac, dst=pkt[Ether].src)

            for i in range(count):
                ether_frame = eth / arp_response
                sendp(ether_frame, iface=iface)


@click.command()
@click.option('--ip', help="Your IP address", required=True)
@click.option('--gateway_ip', help="Gateway IP address", required=True)
@click.option('--iface', help="Network interface", required=True)
def arp_spoof(ip, gateway_ip, iface):
    gateway_mac = get_gateway_mac(gateway_ip, iface)
    if not gateway_mac:
        print("Error: Could not obtain gateway MAC address.")
        return

    print(f"Gateway MAC address: {gateway_mac}")
    my_mac = get_if_hwaddr(iface)
    print(f"My MAC address: {my_mac}")

    fake_mac = generate_random_mac()

    print(f'It is STRONGLY RECOMMENDED TO disable ARP response by the kernel')
    sniff(
        prn=lambda pkt: handle_arp_request(
            pkt, ip, gateway_ip, gateway_mac, fake_mac, iface, my_mac
        ), filter="arp",
        store=0, iface=iface)


if __name__ == '__main__':
    arp_spoof()
