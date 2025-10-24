from ncclient import manager
import xmltodict
import time

def connect(router_ip):
    return manager.connect(
        host=router_ip,
        port=830,
        username="admin",
        password="cisco",
        hostkey_verify=False
    )

def netconf_edit_config(m, netconf_config):
    return m.edit_config(target="running", config=netconf_config)


def check_interface(studentID, router_ip):
    # Idempotence Characteristics of Netconf API
    loopback_name = f"Loopback{studentID}"
    m = connect(router_ip)
    netconf_filter = f"""
    <filter>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{loopback_name}</name>
        </interface>
      </interfaces>
    </filter>
    """
    try:
        netconf_reply = m.get_config(source="running", filter=netconf_filter)
        reply_dict = xmltodict.parse(netconf_reply.xml)
        interfaces = reply_dict.get("rpc-reply", {}).get("data", {}).get("interfaces", {}).get("interface")
        if interfaces:
            return 200
        return 404
    except:
        return 404
    finally:
        m.close_session()


def create(studentID, router_ip, enabled=True):
    # create loopback API with Netconf
    loopback_name = f"Loopback{studentID}"
    if check_interface(studentID, router_ip) == 200:
        return f"Cannot create: Interface {loopback_name} already exists"

    last3 = int(str(studentID)[-3:])
    x = last3 // 100
    y = last3 % 100
    if y == 0:
        y = 1
    ip_addr = f"172.{x}.{y}.1"

    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{loopback_name}</name>
          <description>Interface for student {studentID}</description>
          <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">
            ianaift:softwareLoopback
          </type>
          <enabled>{str(enabled).lower()}</enabled>
          <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
            <address>
              <ip>{ip_addr}</ip>
              <netmask>255.255.255.0</netmask>
            </address>
          </ipv4>
        </interface>
      </interfaces>
    </config>
    """
    m = connect(router_ip)
    try:
        reply = netconf_edit_config(m, netconf_config)
        if "<ok/>" in reply.xml:
            status_str = "enabled" if enabled else "disabled"
            return f"Interface {loopback_name} is created successfully ({status_str}) using Netconf"
        else:
            return f"Cannot create: Interface {loopback_name}"
    except:
        return f"Cannot create: Interface {loopback_name}"
    finally:
        m.close_session()


def delete(studentID, router_ip):
    # delete loopback API with Netconf
    loopback_name = f"Loopback{studentID}"
    if check_interface(studentID, router_ip) != 200:
        return f"Cannot delete: Interface {loopback_name}"

    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface operation="delete">
          <name>{loopback_name}</name>
        </interface>
      </interfaces>
    </config>
    """
    m = connect(router_ip)
    try:
        reply = netconf_edit_config(m, netconf_config)
        if "<ok/>" in reply.xml:
            return f"Interface {loopback_name} is deleted successfully using Netconf"
        else:
            return f"Cannot delete: Interface {loopback_name}"
    except:
        return f"Cannot delete: Interface {loopback_name}"
    finally:
        m.close_session()


def enable(studentID, router_ip):
    # enable loopback API with Netconf
    loopback_name = f"Loopback{studentID}"
    if check_interface(studentID, router_ip) != 200:
        return f"Cannot enable: Interface {loopback_name} does not exist"

    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{loopback_name}</name>
          <enabled>true</enabled>
        </interface>
      </interfaces>
    </config>
    """
    m = connect(router_ip)
    try:
        reply = netconf_edit_config(m, netconf_config)
        if "<ok/>" in reply.xml:
            return f"Interface {loopback_name} is enabled using Netconf"
        return f"Cannot enable: Interface {loopback_name}"
    except:
        return f"Cannot enable: Interface {loopback_name}"
    finally:
        m.close_session()


def disable(studentID, router_ip):
    # disable loopback API with Netconf
    loopback_name = f"Loopback{studentID}"
    if check_interface(studentID, router_ip) != 200:
        return f"Cannot disable: Interface {loopback_name} does not exist"

    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{loopback_name}</name>
          <enabled>false</enabled>
        </interface>
      </interfaces>
    </config>
    """
    m = connect(router_ip)
    try:
        reply = netconf_edit_config(m, netconf_config)
        if "<ok/>" in reply.xml:
            return f"Interface {loopback_name} is disabled using Netconf"
        return f"Cannot disable: Interface {loopback_name}"
    except:
        return f"Cannot disable: Interface {loopback_name}"
    finally:
        m.close_session()


def status(studentID, router_ip):
    # status loopback API with Netconf
    loopback_name = f"Loopback{studentID}"
    time.sleep(1)
    netconf_filter = f"""
    <filter>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{loopback_name}</name>
        </interface>
      </interfaces>
    </filter>
    """
    m = connect(router_ip)
    try:
        reply = m.get_config(source="running", filter=netconf_filter)
        reply_dict = xmltodict.parse(reply.xml)
        interfaces = reply_dict.get("rpc-reply", {}).get("data", {}).get("interfaces", {}).get("interface")
        if not interfaces:
            return f"No Interface {loopback_name} (checked by Netconf)"
        if isinstance(interfaces, list):
            interfaces = interfaces[0]
        enabled = interfaces.get("enabled")
        if enabled == "true":
            return f"Interface {loopback_name} is enabled (checked by Netconf)"
        else:
            return f"Interface {loopback_name} is disabled (checked by Netconf)"
    except:
        return f"No Interface {loopback_name} (checked by Netconf)"
    finally:
        m.close_session()
