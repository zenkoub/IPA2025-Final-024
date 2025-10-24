from netmiko import ConnectHandler
from pprint import pprint
from paramiko.transport import Transport

Transport._preferred_kex = ('diffie-hellman-group14-sha1',)
Transport._preferred_keys = ('ssh-rsa',)

def connect_router(router_ip):
    device_params = {
        "device_type": "cisco_ios",
        "ip": router_ip,
        "username": "admin",
        "password": "cisco",
        "ssh_config_file": False,
        "allow_agent": False,
        "conn_timeout": 30,
        "global_delay_factor": 2,
    }
    return ConnectHandler(**device_params, session_log="netmiko_debug.txt")

def gigabit_status(router_ip):
    ans = ""
    with connect_router(router_ip) as ssh:
        ssh.send_command("terminal length 0")
        up = 0
        down = 0
        admin_down = 0
        
        result = ssh.send_command("show ip interface brief", use_textfsm=True)
        
        interface_status_list = []
        for status in result:
            if status["interface"].startswith("GigabitEthernet"):
                interface_status_list.append(f"{status['interface']} {status['status']}")
                if status["status"] == "up":
                    up += 1
                elif status["status"] == "down":
                    down += 1
                elif status["status"] == "administratively down":
                    admin_down += 1
        
        ans = (
            ", ".join(interface_status_list)
            + f" -> {up} up, {down} down, {admin_down} administratively down"
        )
        pprint(ans)
        return ans
