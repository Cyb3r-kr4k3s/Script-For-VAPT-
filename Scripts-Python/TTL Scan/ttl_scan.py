#!/usr/bin/python3
# coding: utf-8

# Identifies the OS and Device Network through TimeToLive (TTL)
import re
import sys
import subprocess
from tabulate import tabulate
from termcolor import colored
import pyfiglet

def get_ttl(ip_address):
    try:
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
    elif ttl == 255:
        return "Cisco Routers"
    elif ttl == 254:
        return "Solaris/AIX"
    else:
        return "Not Found"

def save_to_file(ip_address, ttl, os_name):
    with open("TTLResult.txt", "w") as file:
        file.write(f"IP Address: {ip_address}\nTTL: {ttl}\nOS: {os_name}\n")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(colored(f"\n[!] Uso: {sys.argv[0]} <direccion-ip>\n", "yellow"))
        sys.exit(1)

    ip_address = sys.argv[1]
    ttl = get_ttl(ip_address)
    os_name = get_os(ttl)

    banner = pyfiglet.figlet_format("Dev by Cyb3r-kr4k3s", font="slant")
    colored_banner = colored(banner, "green")
    print(colored_banner)

    print(colored("\nIdentified Time To Live\n", "green", attrs=["bold"]))

    table = [["IP Address", ip_address], ["TTL", ttl], ["OS", os_name]]
    print(colored(tabulate(table, headers=["Informational", "Value"], tablefmt="grid"), "cyan"))

    save_to_file(ip_address, ttl, os_name)
    print(colored("\nResult saved to 'TTLResult.txt'\n", "green"))
