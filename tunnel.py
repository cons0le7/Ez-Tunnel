import subprocess
import threading
import socket
import re
import time
import signal
import sys
import os
import pwd
from queue import Queue, Empty

RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"

ssh_process = None
shutdown_flag = False
serveo_url = None
CURRENT_USER = pwd.getpwuid(os.getuid()).pw_name


print(f"""{GREEN} 

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠚⠉⠀⠀⠉⠑⢦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠞⠀⠀⠀⠀⠀⠀⠀⠀⠱⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡜⠀⠀⠀⠀⠀⣀⣀⠀⠀⠀⠀⠀⢣⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⣠⠔⠋⠉⣩⣍⠉⠙⠢⣄⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢧⡜⢏⠓⠒⠚⠁⠈⠑⠒⠚⣹⢳⡸⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠘⣆⠸⡄⠀⠀⠀⠀⠀⠀⢠⠇⣰⠃⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⡴⠚⠉⢣⡙⢦⡀⠀⠀⢀⡰⢋⡜⠉⠓⠦⣀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⡴⠁⢀⣀⣀⣀⣙⣦⣉⣉⣋⣉⣴⣋⣀⣀⣀⡀⠈⢧⠀⠀⠀⠀⠀
⠀⠀⠀⠀⡸⠁⠀⢸⠀⠀⠀⠀⢀⣔⡛⠛⡲⡀⠀⠀⠀⠀⡇⠀⠈⢇⠀⠀⠀⠀
⠀⠀⠀⢠⠇⠀⠀⠸⡀⠀⠀⠀⠸⣼⠽⠯⢧⠇⠀⠀⠀⠀⡇⠀⠀⠘⡆⠀⠀⠀
⠀⠀⠀⣸⠀⠀⠀⠀⡇⠀⠀⠀⠳⢼⡦⢴⡯⠞⠀⠀⠀⢰⠀⠀⠀⠀⢧⠀⠀⠀
⠀⠀⠀⢻⠀⠀⠀⠀⡇⠀⠀⠀⢀⡤⠚⠛⢦⣀⠀⠀⠀⢸⠀⠀⠀⠀⡼⠀⠀⠀
⠀⠀⠀⠈⠳⠤⠤⣖⣓⣒⣒⣒⣓⣒⣒⣒⣒⣚⣒⣒⣒⣚⣲⠤⠤⠖⠁⠀⠀⠀
⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ▄▖    ▄▖        ▜ 
        ▙▖▀▌▄▖▐ ▌▌▛▌▛▌█▌▐ 
        ▙▖▙▖  ▐ ▙▌▌▌▌▌▙▖▐▖
                                                                                       
{RESET}""")

while True:
    try:
        PORT = int(input(f"{CYAN}Enter server port (default 3000): {RESET}") or "3000")
        if PORT <= 0 or PORT > 65535:
            print(f"{RED}Invalid port number. Try again.{RESET}")
            continue
        break
    except ValueError:
        print(f"{RED}Please enter a valid number.{RESET}")

def check_port(port):
    try:
        result = subprocess.run(["lsof", "-i", f":{port}"], stdout=subprocess.PIPE, text=True)
        lines = result.stdout.strip().split("\n")[1:] 
        processes = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                processes.append((int(parts[1]), parts[2], parts[0])) 
        return processes
    except Exception:
        return []

def kill_port_processes(processes):
    print(f"\n{GREEN}Killing processes on port {PORT}:{RESET}")
    for pid, user, cmd in processes:
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.2)
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            print(f"\n{GREEN}Killed PID {pid} ({cmd}){RESET}")
        except Exception as e:
            print(f"\n{RED}Failed to kill PID {pid}: {e}{RESET}")

procs = check_port(PORT)
if procs:
    print(f"\n{YELLOW}Port {PORT} is in use by the following processes:{RESET}\n")
    for pid, user, cmd in procs:
        print(f"  PID: {pid}, User: {user}, Command: {cmd}")
    choice = input(f"\n{CYAN}Do you want to kill these processes? (y/N): {RESET}").strip().lower()
    if choice == "y":
        kill_port_processes(procs)
        time.sleep(0.5)
        if check_port(PORT):
            print(f"\n{RED}Port {PORT} still in use. Exiting.{RESET}")
            sys.exit(1)
    else:
        print(f"\n{YELLOW}Skipping process kill. If the port is busy, the server may fail to start.{RESET}")
else:
    print(f"\n{GREEN}Port {PORT} is free.{RESET}")

def shutdown(sig=None, frame=None):
    global shutdown_flag
    if shutdown_flag:
        return
    shutdown_flag = True
    print(f"\n\n{RED}Shutting down...{RESET}")
    for proc, name in [(server, "Node server"), (ssh_process, "SSH tunnel")]:
        if proc is None:
            continue
        try:
            proc.terminate()
            proc.wait(timeout=5)
            print(f"{RED}{name} terminated.{RESET}")
        except Exception:
            try:
                proc.kill()
                print(f"{YELLOW}{name} killed.{RESET}")
            except Exception:
                print(f"{RED}Failed to terminate {name}.{RESET}")
    leftover_procs = check_port(PORT)
    if leftover_procs:
        print(f"\n{YELLOW}Some processes are still using port {PORT}. Killing them...{RESET}")
        kill_port_processes(leftover_procs)
    print(f"{GREEN}\n - Shutdown Complete - \n{RESET}")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

try:
    server = subprocess.Popen(
        ["node", "server.js"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
except Exception as e:
    print(f"{RED}Failed to start Node server: {e}{RESET}")
    sys.exit(1)

def enqueue_output(process, queue):
    for line in iter(process.stdout.readline, ''):
        queue.put(line)
    process.stdout.close()
node_queue = Queue()
threading.Thread(target=enqueue_output, args=(server, node_queue), daemon=True).start() 
timeout = 10
start_time = time.time()
while time.time() - start_time < timeout:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("127.0.0.1", PORT))
        s.close()
        print(f"\n{MAGENTA}Node server is listening on port {PORT}{RESET}")
        break
    except ConnectionRefusedError:
        time.sleep(0.2)
else:
    print(f"{RED}Node server did not start within {timeout} seconds{RESET}")
    server.terminate()
    sys.exit(1)
    
print(f"\n{CYAN}Select tunneling service:{RESET}\n")
print(f"{YELLOW}[1]{CYAN} - {GREEN}Serveo.net{RESET}")
print(f"{YELLOW}[2]{CYAN} - {GREEN}localhost.run{RESET}")

while True:
    tunnel_choice = input(f"\n{GREEN}>>> {RESET}").strip()
    if tunnel_choice == "1":
        ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-R", f"80:127.0.0.1:{PORT}", "serveo.net"]
        url_regex = r'https?://[^\s]*\.serveo\.net'
        break
    elif tunnel_choice == "2":
        ssh_cmd = [
            "ssh", "-o", "StrictHostKeyChecking=no",
            "-o", "ServerAliveInterval=60",
            "-R", f"80:127.0.0.1:{PORT}",
            "nokey@localhost.run"
        ]
        url_regex = r'https://[a-z0-9]+\.lhr\.life'
        break
    else:
        print(f"{YELLOW}Invalid choice, try again.{RESET}")
        
print(f"\n{MAGENTA}Ctrl+C twice to shutdown.{RESET}\n")

ssh_process = subprocess.Popen(
    ssh_cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

ssh_queue = Queue()
threading.Thread(target=enqueue_output, args=(ssh_process, ssh_queue), daemon=True).start()

try:
    while not shutdown_flag: 
        try:
            line = node_queue.get(timeout=0.1)
            print(line, end='')
        except Empty:
            pass
        try:
            line = ssh_queue.get(timeout=0.1)
            print(line, end='')
            if serveo_url is None:
                match = re.search(url_regex, line)
                if match:
                    serveo_url = match.group(0)
                    print(f"\n{CYAN}Tunnel URL:{RESET} {MAGENTA}{serveo_url}{RESET}\n")
        except Empty:
            pass

        if server.poll() is not None and ssh_process.poll() is not None:
            break
except Exception as e:
    print(f"{RED}Error: {e}{RESET}")
finally:
    shutdown()
