import subprocess
import re
import argparse
import requests
from tabulate import tabulate
from colorama import init, Fore, Style
import pyfiglet
from termcolor import colored

# Initialize colorama
init()

def parse_ntlm_info(output):
    """Parse NTLM info from nmap output."""
    patterns = {
        "Target Name": r"Target_Name:\s*(\S+)",
        "NetBIOS Domain Name": r"NetBIOS_Domain_Name:\s*(\S+)",
        "NetBIOS Computer Name": r"NetBIOS_Computer_Name:\s*(\S+)",
        "DNS Domain Name": r"DNS_Domain_Name:\s*(\S+)",
        "DNS Computer Name": r"DNS_Computer_Name:\s*(\S+)",
        "DNS Tree Name": r"DNS_Tree_Name:\s*(\S+)",
        "Product Version": r"Product_Version:\s*(\S+)"
    }

    ntlm_info = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        ntlm_info[key] = match.group(1) if match else None

    return ntlm_info

def build_cpe(ntlm_info):
    """Build Common Platform Enumeration (CPE) string."""
    vendor = "Microsoft"
    product = "Windows"
    version = ntlm_info.get("Product Version", "unspecified").lower()
    return f"cpe:2.3:a:{vendor.lower()}:{product.lower()}:{version}"

def run_nmap_script(ip_address, port, script_name):
    """Run specified nmap script and return the output."""
    result = subprocess.run(
        ["nmap", "-p", str(port), "--script", script_name, ip_address],
        capture_output=True, text=True
    )
    return result.stdout

def get_cves_for_cpe(cpe_name):
    """Fetch CVEs for a given CPE from NVD."""
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    search_url = f"{base_url}?cpeName={cpe_name}"

    response = requests.get(search_url)
    if response.status_code == 200:
        cve_data = response.json()
        vulnerabilities = cve_data.get("vulnerabilities", [])
        return [cve["cve"]["id"] for cve in vulnerabilities]
    else:
        print(f"Error: Unable to fetch CVEs. Status code: {response.status_code}")
        return []

def get_cve_details(cve_id):
    """Fetch detailed information about a CVE from MITRE."""
    search_url = f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve_id}"
    response = requests.get(search_url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error: Unable to fetch CVE details. Status code: {response.status_code}")
        return ""

def format_output(ntlm_info, cpe, enum_encryption_output, cves):
    """Format the output for readability and color."""
    table_data = [
        ["Information", "Found Data"],
        ["Target Name", ntlm_info['Target Name']],
        ["NetBIOS Domain Name", ntlm_info['NetBIOS Domain Name']],
        ["NetBIOS Computer Name", ntlm_info['NetBIOS Computer Name']],
        ["DNS Domain Name", ntlm_info['DNS Domain Name']],
        ["DNS Computer Name", ntlm_info['DNS Computer Name']],
        ["DNS Tree Name", ntlm_info['DNS Tree Name']],
        ["Product Version", ntlm_info['Product Version']],
        ["CPE", cpe]
    ]

    cve_table_data = [["CVE ID", "Description"]]
    for cve in cves:
        details = get_cve_details(cve)
        cve_table_data.append([cve, details])

    # Tables with colors
    table = tabulate(table_data, headers="firstrow", tablefmt="fancy_grid")
    cve_table = tabulate(cve_table_data, headers="firstrow", tablefmt="fancy_grid")

    table_colored = f"{Fore.CYAN}{table}{Style.RESET_ALL}"
    cve_table_colored = f"{Fore.GREEN}{cve_table}{Style.RESET_ALL}"

    return f"{table_colored}\n\n------------------- RDP Reconnaissance Results -------------------\n{Fore.YELLOW}{enum_encryption_output}{Style.RESET_ALL}\n\n------------------------ CVEs Identified------------------------\n{cve_table_colored}"

def scan_rdp(ip_address, port, output_file):
    try:
        # Run rdp-ntlm-info script
        ntlm_info_output = run_nmap_script(ip_address, port, "rdp-ntlm-info")
        ntlm_info = parse_ntlm_info(ntlm_info_output)
        cpe = build_cpe(ntlm_info)

        # Run rdp-enum-encryption script
        enum_encryption_output = run_nmap_script(ip_address, port, "rdp-enum-encryption")

        # Get CVEs for the given CPE
        cves = get_cves_for_cpe(cpe)

        # Format and save the output
        formatted_output = format_output(ntlm_info, cpe, enum_encryption_output, cves)

        # Print the banner
        banner = pyfiglet.figlet_format("Dev by Cyb3r-kr4k3s", font="slant")
        colored_banner = colored(banner, "green")
        print(colored_banner)

        with open(output_file, 'w') as f:
            f.write(formatted_output)

        print(formatted_output)

        print("Scan successful. Results saved to", output_file)

    except Exception as e:
        print("Error:", e)

def main():
    parser = argparse.ArgumentParser(description="RDP Scanner")
    parser.add_argument("ip_address", help="IP address to scan")
    parser.add_argument("port", type=int, help="Port to scan")
    parser.add_argument("output_file", help="Output file path")
    args = parser.parse_args()

    scan_rdp(args.ip_address, args.port, args.output_file)

if __name__ == "__main__":
    main()
