import asyncio
import socket
from typing import List, Tuple
from tabulate import tabulate
from termcolor import colored

def process_range(port_range: str) -> List[int]:
    ports = []
    blocks = port_range.split(',')
    for block in blocks:
        if '-' in block:
            min_port, max_port = map(int, block.split('-'))
            ports.extend(range(min_port, max_port + 1))
        else:
            ports.append(int(block))
    return ports

async def scan_port(host: str, port: int, timeout: float) -> Tuple[int, str]:
    conn = asyncio.open_connection(host, port)
    try:
        reader, writer = await asyncio.wait_for(conn, timeout)
        writer.close()
        await writer.wait_closed()
        return (port, "Open")
    except asyncio.TimeoutError:
        return (port, "Filtered")
    except ConnectionRefusedError:
        return (port, "Close")
    except Exception as e:
        return (port, f"Error: {e}")

async def bound_scan(semaphore, host, port, timeout):
    async with semaphore:
        return await scan_port(host, port, timeout)

async def main():
    host = input("Enter Host or IP address to scan: ")
    port_range = input("Enter the range of ports to scan (e.g., 80,443,1-65535,1000-2000): ")
    threads = int(input("Enter the thread count to be used: "))
    timeout = float(input("Enter the timeout per port (in seconds): "))

    ports = process_range(port_range)
    print(f"\n[*] Escaneando host {host} (Puertos: {port_range})\n")

    semaphore = asyncio.Semaphore(threads)
    tasks = [bound_scan(semaphore, host, port, timeout) for port in ports]
    results = []

    for future in asyncio.as_completed(tasks):
        port, status = await future
        if status == "Open":
            results.append([port, colored("Open", "green")])
        elif status == "Filtered":
            results.append([port, colored("Filtered", "yellow")])

    if results:
        headers = ["Port", "Status"]
        print(tabulate(results, headers=headers, tablefmt="grid"))
    else:
        print("No Open & Filtered Ports Found.")

if __name__ == "__main__":
    asyncio.run(main())

