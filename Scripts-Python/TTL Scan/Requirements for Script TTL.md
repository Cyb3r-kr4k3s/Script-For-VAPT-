## Script Detailed Steps ↓

### 1. Sending the Ping Request:
#### The script uses subprocess.check_output to execute the ping command.
#### The command sends an ICMP Echo Request packet to the specified IP address.

### 2. Extracting the TTL Value:
#### The output of the ping command is captured and analyzed.
#### A regular expression (`re.search(r”ttl=(\d+)”, output).group(1)`) is used to extract the TTL value from the output string.

### 3. Inferring the OS:
#### The extracted TTL value is compared against known default values for different operating systems.
#### The script returns the OS name based on the TTL value.

### TTL Script ↓
#### Summary of how you can install each package:
re and sys are built-in Python modules, so you don't need to install them.
subprocess is also a built-in Python module, so no installation is necessary.
tabulate, termcolor, and pyfiglet need to be installed using pip:

### Requirements for Script:

`pip install pyfiglet termcolor tabulate`
