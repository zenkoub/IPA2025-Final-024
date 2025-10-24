import json
import requests
requests.packages.urllib3.disable_warnings()

router_ip = "10.0.15.64"

api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface="
api_url_status = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces-state/interface="

headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

basicauth = ("admin", "cisco")

def check_interface(loopback_name, retries=3):
    url = api_url + loopback_name
    for i in range(retries):
        resp = requests.get(url, auth=basicauth, headers=headers, verify=False)
        if resp.status_code == 200:
            return 200
    print(f"Checking {loopback_name}: {resp.status_code}, {resp.text}")
    return resp.status_code


def create(studentID):
    loopback_name = f"Loopback{studentID}"
    if check_interface(loopback_name) == 200:
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
        return f"Interface {loopback_name} is created successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


def delete(studentID):
    loopback_name = f"Loopback{studentID}"
    if check_interface(loopback_name) != 200:
        return f"Cannot delete: Interface {loopback_name}"
    
    resp = requests.delete(
        api_url + loopback_name,
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {loopback_name} is deleted successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


def enable(studentID):
    loopback_name = f"Loopback{studentID}"
    if check_interface(loopback_name) != 200:
        return f"Cannot enable: Interface {loopback_name}"
    
    yangConfig = {
        "ietf-interfaces:interface": {
            "enabled": True
        }
    }

    resp = requests.patch(
        api_url + loopback_name,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {loopback_name} is enabled successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


def disable(studentID):
    loopback_name = f"Loopback{studentID}"
    if check_interface(loopback_name) != 200:
        return f"Cannot shutdown: Interface {loopback_name}"
    
    yangConfig = {
        "ietf-interfaces:interface": {
            "enabled": False
        }
    }

    resp = requests.patch(
        api_url + loopback_name,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {loopback_name} is disabled successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


def status(studentID):
    loopback_name = f"Loopback{studentID}"
    url = api_url_status + loopback_name

    resp = requests.get(url, auth=basicauth, headers=headers, verify=False)

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        response_json = resp.json()
        admin_status = response_json["ietf-interfaces:interface"]["admin-status"]
        oper_status = response_json["ietf-interfaces:interface"]["oper-status"]
        if admin_status == 'up' and oper_status == 'up':
            return f"Interface {loopback_name} is enabled"
        elif admin_status == 'down' and oper_status == 'down':
            return f"Interface {loopback_name} is disabled"
    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return f"No Interface {loopback_name}"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
