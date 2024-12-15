#!/usr/bin/python3
# coding: utf-8

# Identifies the OS and Device Network through TimeToLive (TTL) and Subnet Classes
import re
import sys
import subprocess
from tabulate import tabulate
from termcolor import colored
import pyfiglet

def get_ttl(ip_address):
    try:
        # Check if the address is IPv6 or IPv4
        if ":" in ip_address:
            output = subprocess.check_output(["ping6", "-c", "1", ip_address], stderr=subprocess.STDOUT, universal_newlines=True)
        else:
            output = subprocess.check_output(["ping", "-c", "1", ip_address], stderr=subprocess.STDOUT, universal_newlines=True)
        ttl_value = re.search(r"ttl=(\d+)", output).group(1)
        return ttl_value
    except subprocess.CalledProcessError:
        print(colored(f"Error: Could not ping IP address {ip_address}", "red"))
        sys.exit(1)
    except AttributeError:
        print(colored("Error: Could not retrieve TTL value", "red"))
        sys.exit(1)

def get_os(ttl):
    ttl = int(ttl)
    if ttl == 128:
        return "Windows"
    elif ttl == 64:
        return "Linux/macOS/FreeBSD/Juniper Routers/HP-UX/Apple iOS/Android OS"
    elif ttl == 254:
        return "Solaris/AIX"
    elif ttl == 255:
        return "Cisco Routers"
    else:
        return "Not Found"

def get_subnet_class(ip_address):
    if ":" in ip_address:
        return "IPv6 - No subnet classes"
    octets = list(map(int, ip_address.split('.')))
    if octets[0] < 128:
        return "Class A"
    elif octets[0] < 192:
        return "Class B"
    elif octets[0] < 224:
        return "Class C"
    elif octets[0] < 240:
        return "Class D"
    elif octets[0] < 256:
        return "Class E"
    else:
        return "Invalid IP Address"

def is_private_ip(ip_address):
    octets = list(map(int, ip_address.split('.')))
    if (octets[0] == 10 or
        (octets[0] == 172 and 16 <= octets[1] <= 31) or
        (octets[0] == 192 and octets[1] == 168)):
        return "Private"
    else:
        return "Public"

def save_to_file(ip_address, ttl, os_name, subnet_class, address_type):
    with open("TTLResult.txt", "w") as file:
        file.write(f"IP Address: {ip_address}\nTTL: {ttl}\nOS: {os_name}\nSubnet Class: {subnet_class}\nAddress Type: {address_type}\n")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(colored(f"\n[!] Uso: {sys.argv[0]} <IP-Address>\n", "yellow"))
        sys.exit(1)

    ip_address = sys.argv[1]
    ttl = get_ttl(ip_address)
    os_name = get_os(ttl)
    subnet_class = get_subnet_class(ip_address)
    address_type = is_private_ip(ip_address)

    banner = pyfiglet.figlet_format("Dev by Cyb3r-kr4k3s", font="slant")
    colored_banner = colored(banner, "green")
    print(colored_banner)

    print(colored("\nIdentified Time To Live\n", "green", attrs=["bold"]))

    table = [["IP Address", ip_address], ["TTL", ttl], ["OS", os_name], ["Subnet Class", subnet_class], ["Address Type", address_type]]
    print(colored(tabulate(table, headers=["Informational", "Value"], tablefmt="grid"), "cyan"))

    print(colored("\nExplanation of Subnet Classes:\n", "green", attrs=["bold"]))
    explanation = """
    - Class A: IP addresses with the first octet ranging from 1 to 126.
    - Class B: IP addresses with the first octet ranging from 128 to 191.
    - Class C: IP addresses with the first octet ranging from 192 to 223.
    - Class D: IP addresses with the first octet ranging from 224 to 239, used for multicasting.
    - Class E: IP addresses with the first octet ranging from 240 to 255, reserved for future use or research and development.
    """
    print(colored(explanation, "cyan"))

    print(colored("\nAddress Types:\n", "green", attrs=["bold"]))
    address_types_explanation = """
    - Private: IP addresses used within a private network. They are not routable on the internet.
    - Public: IP addresses that are routable on the internet.
    """
    print(colored(address_types_explanation, "cyan"))

    save_to_file(ip_address, ttl, os_name, subnet_class, address_type)
    print(colored("\nResult saved to 'TTLResult.txt'\n", "green"))
