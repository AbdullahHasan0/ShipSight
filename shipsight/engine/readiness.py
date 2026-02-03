import socket
import time
import httpx
from rich.console import Console
import subprocess

console = Console()

def is_port_open(host: str, port: int) -> bool:
    """Check if a port is open. Tries IPv4 and IPv6 if host is localhost."""
    targets = [host]
    if host == "localhost":
        targets = ["127.0.0.1", "::1"]
        
    for target in targets:
        # Determine address family
        family = socket.AF_INET6 if ":" in target else socket.AF_INET
        with socket.socket(family, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            try:
                s.connect((target, port))
                return True
            except (socket.timeout, ConnectionRefusedError, OSError):
                continue
    return False

def wait_for_ready(host: str, port: int, timeout: int = 120) -> bool:
    start_time = time.time()
    console.print(f"[yellow]Waiting for {host}:{port} to become ready (Timeout: {timeout}s)...[/yellow]")
    
    while time.time() - start_time < timeout:
        if is_port_open(host, port):
            # Try both IPv4 and IPv6 for HTTP check
            ips = ["127.0.0.1", "::1"] if host == "localhost" else [host]
            for ip in ips:
                try:
                    url = f"http://[{ip}]:{port}" if ":" in ip else f"http://{ip}:{port}"
                    response = httpx.get(url, timeout=2.0, follow_redirects=True)
                    # Any HTTP response means the server is alive
                    console.print(f"[green]Service is ready at {url} (Status: {response.status_code})[/green]")
                    return True
                except (httpx.RequestError, httpx.HTTPStatusError):
                    pass
        time.sleep(2.0)
    
    return False

def discover_ports(pid: int) -> list[int]:
    """Find all ports that a process (and its children) is listening on recursively."""
    import os
    ports = set()
    
    if os.name == "nt":
        def get_all_child_pids(parent_pid):
            all_pids = {parent_pid}
            try:
                # Use wmic to find children of this specific PID
                res = subprocess.run(f"wmic process where (ParentProcessId={parent_pid}) get ProcessId", shell=True, capture_output=True, text=True)
                for line in res.stdout.splitlines():
                    clean_line = line.strip()
                    if clean_line.isdigit():
                        child_pid = int(clean_line)
                        if child_pid != parent_pid: # Prevent infinite recursion
                            all_pids.update(get_all_child_pids(child_pid))
            except: pass
            return all_pids

        try:
            # 1. Map out the entire process tree
            all_tree_pids = get_all_child_pids(pid)
            
            # 2. Get netstat info once for performance
            res = subprocess.run("netstat -ano", shell=True, capture_output=True, text=True)
            for line in res.stdout.splitlines():
                if "LISTENING" in line:
                    parts = line.split()
                    if len(parts) > 4:
                        try:
                            listening_pid = int(parts[-1])
                            if listening_pid in all_tree_pids:
                                addr = parts[1] # e.g. [::]:5173 or 0.0.0.0:3000
                                port_str = addr.split(":")[-1]
                                if port_str.isdigit():
                                    port = int(port_str)
                                    if port > 1024: # Skip system ports
                                        ports.add(port)
                        except (ValueError, IndexError): continue
        except: pass
    else:
        # Linux/Mac
        try:
            res = subprocess.run(f"lsof -nP -iTCP -sTCP:LISTEN -p {pid}", shell=True, capture_output=True, text=True)
            for line in res.stdout.split("\n")[1:]:
                if ":" in line:
                    port = int(line.split(":")[-1].split()[0])
                    ports.add(port)
        except: pass
        
    return sorted(list(ports))

def auto_wait_for_ready(host: str, initial_port: int, process: 'subprocess.Popen', timeout: int = 120) -> tuple[int, str]:
    """Wait for readiness. Returns (port, url) of the working service."""
    start_time = time.time()
    console.print(f"[yellow]Waiting for project at {host} (Timeout: {timeout}s)...[/yellow]")
    
    announced_ports = set()
    pid = process.pid
    
    ips = ["127.0.0.1", "::1"] if host == "localhost" else [host]
    
    # Special Case: No port required (Scripts)
    if not initial_port:
        console.print("[blue]No port specified. Monitoring script execution...[/blue]")
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                if process.returncode == 0:
                    console.print("[green]Project script completed successfully.[/green]")
                    return -1, "script"
                console.print(f"[red]Project script failed (Exit Code: {process.returncode}).[/red]")
                return 0, ""
            time.sleep(1.0)
        return 0, ""

    while time.time() - start_time < timeout:
        # 0. Check if process is still alive
        if process.poll() is not None:
            if process.returncode == 0:
                console.print("[green]Project script completed successfully.[/green]")
                return -1, "script"
            console.print(f"[red]Project process terminated prematurely (Exit Code: {process.returncode}).[/red]")
            return 0, ""

        # 1. Gather all candidates
        candidates = []
        if initial_port:
            candidates.append(initial_port)
        candidates.extend(discover_ports(pid))
        
        for p in candidates:
            if p not in announced_ports:
                console.print(f"[blue]Checking port: {p}[/blue]")
                announced_ports.add(p)
            
            for ip in ips:
                if is_port_open(ip, p):
                    try:
                        url = f"http://[{ip}]:{p}" if ":" in ip else f"http://{ip}:{p}"
                        response = httpx.get(url, timeout=2.0, follow_redirects=True)
                        # Any HTTP response means the server is alive
                        console.print(f"[green]Detected working service at {url} (Status: {response.status_code})[/green]")
                        return p, url
                    except: pass
        
        time.sleep(2.0)
    
    console.print(f"[red]Timeout: Project failed to respond on any port within {timeout}s.[/red]")
    return 0, ""
