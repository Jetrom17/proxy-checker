print('''
Have a coffee, this might take a while. Try checking the processes, like 'htop' for instance.

                      (
                        )     (
                 ___...(-------)-....___
             .-""       )    (          ""-.
       .-'``'|-._             )         _.-|
      /  .--.|   `""---...........---""`   |
     /  /    |                             |
     |  |    |                             |
      \  \   |                             |
       `\ `\ |                             |
         `\ `|                             |
         _/ /\                             /
        (__/  \                           /
     _..---""` \                         /`""---.._
  .-'           \                       /          '-.
 :               `-.__             __.-'              :
 :                  ) ""---...---"" (                 :
  '._               `"--...___...--"`              _.'
    \""--..__                              __..--""/
     '._     """----.....______.....----"""     _.'
        `""--..,,_____            _____,,..--""`
                      `"""----"""`
''')


# print('''
# Tests conducted:
#
# ~5 proxies ~17s
# ~70 proxies ~30s
# ~100 proxies ~48s
# ~500 proxies ~1:27m
# ~800 proxies ~2:30m
# ''')

# Requirements.txt
import concurrent.futures
from termcolor import colored
import subprocess

def check_ip(ip):
    # Check if the port is specified and remove it for verification
    if ":" in ip:
        ip_without_port = ip.split(":")[0]
    else:
        ip_without_port = ip

    # Run the ping
    try:
        output = subprocess.check_output(['ping', '-c', '1', '-W', '7', ip_without_port], universal_newlines=True, timeout=7)
        return ip, True
    except subprocess.TimeoutExpired:
        return ip, False
    except subprocess.CalledProcessError as e:
        # Ignore error "Time to live exceeded"
        if "Time to live exceeded" in e.output:
            return ip, False
        else:
            raise e

# Read proxy.txt and run
with open('proxy.txt', 'r') as file:
    ips_to_check = [ip.strip() for ip in file.readlines()]

# Check IPs in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = {executor.submit(check_ip, ip): ip for ip in ips_to_check}
  
ips_alive = []
ips_to_save = []
count = 1
for future in concurrent.futures.as_completed(results):
    ip = results[future]
    try:
        ip, is_alive = future.result()
        if is_alive:
            print(colored(f"IP-{count}: {ip} is {colored('on', 'green')}.", 'green'))
            ips_alive.append(ip)
            ips_to_save.append(ip)
        else:
            print(colored(f"IP-{count}: {ip} is {colored('dead', 'red')}.", 'red'))
        count += 1
    except Exception as e:
        print(f"Error while checking the IP {ip}: {e}")

# Question about saving live IPs...
save_to_file = input("Do you want to save the live IPs to the file? (y/n): ").lower()
if save_to_file == 'y':
    with open('IP_life.txt', 'w') as file:
        for ip in ips_alive:
            ip_without_port = ip.split(":")[0]  # Remove the port
            file.write(ip_without_port + '\n')
          
# Question about saving live IPs with port...
save_full_info = input("Do you want to save the live IPs with ports to the file? (y/n): ").lower()
if save_full_info == 'y':
    with open('IP_life_with_port.txt', 'w') as file: # No remove the port
        for ip in ips_to_save:
            file.write(ip + '\n')
