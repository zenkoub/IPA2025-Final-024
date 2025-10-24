import json
import requests
requests.packages.urllib3.disable_warnings()

headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

basicauth = ("admin", "cisco")

router_method = None

def check_interface(loopback_name, router_ip, retries=3):
    # Idempotence Characteristics of Restconf API
    api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface="
    for i in range(retries):
        resp = requests.get(api_url + loopback_name, auth=basicauth, headers=headers, verify=False)
        if resp.status_code == 200:
            return 200
    print(f"Checking {loopback_name}: {resp.status_code}, {resp.text}")
    return resp.status_code


def create(studentID, router_ip):
    loopback_name = f"Loopback{studentID}"
    if check_interface(loopback_name, router_ip) == 200:
        return f"Cannot create: Interface {loopback_name}"

    last3 = int(str(studentID)[-3:])
    x = last3 // 100
    y = last3 % 100
    if y == 0:
        y = 1
    ip_addr = f"172.{x}.{y}.1"
    
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": loopback_name,
            "description": f"Interface for student {studentID}",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [{"ip": ip_addr, "netmask": "255.255.255.0"}]
            }
        }
    }

    api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface="
    resp = requests.put(
        api_url + loopback_name,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False
    )
    
    print("PUT Response:", resp.status_code, resp.text)
    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {loopback_name} is created successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot create: Interface {loopback_name}"


def delete(studentID, router_ip):
    loopback_name = f"Loopback{studentID}"
    if check_interface(loopback_name, router_ip) != 200:
        return f"Cannot delete: Interface {loopback_name}"
    
    api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface="
    resp = requests.delete(
        api_url + loopback_name,
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {loopback_name} is deleted successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot delete: Interface {loopback_name}"


def enable(studentID, router_ip):
    loopback_name = f"Loopback{studentID}"
    if check_interface(loopback_name, router_ip) != 200:
        return f"Cannot enable: Interface {loopback_name}"
    
    yangConfig = {
        "ietf-interfaces:interface": {
            "enabled": True
        }
    }

    api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface="
    resp = requests.patch(
        api_url + loopback_name,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {loopback_name} is enabled successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot enable: Interface {loopback_name}"


def disable(studentID, router_ip):
    loopback_name = f"Loopback{studentID}"
    if check_interface(loopback_name, router_ip) != 200:
        return f"Cannot shutdown: Interface {loopback_name} (checked by Restconf)"
    
    yangConfig = {
        "ietf-interfaces:interface": {
            "enabled": False
        }
    }

    api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface="
    resp = requests.patch(
        api_url + loopback_name,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {loopback_name} is disabled successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot shutdown: Interface {loopback_name} (checked by Restconf)"


def status(studentID, router_ip):
    loopback_name = f"Loopback{studentID}"
    api_url_status = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces-state/interface="

    resp = requests.get(api_url_status + loopback_name, auth=basicauth, headers=headers, verify=False)

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        response_json = resp.json()
        admin_status = response_json["ietf-interfaces:interface"]["admin-status"]
        oper_status = response_json["ietf-interfaces:interface"]["oper-status"]
        if admin_status == 'up' and oper_status == 'up':
            return f"Interface {loopback_name} is enabled (checked by Restconf)"
        elif admin_status == 'down' and oper_status == 'down':
            return f"Interface {loopback_name} is disabled (checked by Restconf)"
    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return f"No Interface {loopback_name} (checked by Restconf)"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
