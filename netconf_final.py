from ncclient import manager
import xmltodict

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
        netconf_reply = m.get(netconf_filter)
        reply_dict = xmltodict.parse(netconf_reply.xml)
        if "data" in reply_dict and "interfaces" in reply_dict["data"]:
            return 200
        else:
            return 404
    except:
        return 404
    finally:
        m.close_session()


def create(studentID, router_ip):
    loopback_name = f"Loopback{studentID}"
    if check_interface(studentID, router_ip) == 200:
        return f"Cannot create: Interface {loopback_name}"

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
          <enabled>true</enabled>
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
            return f"Interface {loopback_name} is created successfully using Netconf"
        else:
            return f"Cannot create: Interface {loopback_name}"
    except:
        return f"Cannot create: Interface {loopback_name}"
    finally:
        m.close_session()


def delete(studentID, router_ip):
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
    loopback_name = f"Loopback{studentID}"
    if check_interface(studentID, router_ip) != 200:
        return f"Cannot enable: Interface {loopback_name}"

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
          <enabled>true</enabled>
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
            return f"Interface {loopback_name} is enabled successfully using Netconf"
        else:
            return f"Cannot enable: Interface {loopback_name}"
    except Exception as e:
        return f"Cannot enable: Interface {loopback_name} ({str(e)})"
    finally:
        m.close_session()


def disable(studentID, router_ip):
    loopback_name = f"Loopback{studentID}"
    if check_interface(studentID, router_ip) != 200:
        return f"Cannot shutdown: Interface {loopback_name} (checked by Netconf)"

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
            return f"Interface {loopback_name} is shutdowned successfully using Netconf"
        else:
            return f"Cannot shutdown: Interface {loopback_name} (checked by Netconf)"
    except:
        return f"Cannot shutdown: Interface {loopback_name} (checked by Netconf)"
    finally:
        m.close_session()


def status(studentID, router_ip):
    loopback_name = f"Loopback{studentID}"
    netconf_filter = f"""
    <filter>
      <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{loopback_name}</name>
        </interface>
      </interfaces-state>
    </filter>
    """
    m = connect(router_ip)
    try:
        reply = m.get(netconf_filter)
        reply_dict = xmltodict.parse(reply.xml)
        if ("data" in reply_dict and
            "interfaces-state" in reply_dict["data"] and
            "interface" in reply_dict["data"]["interfaces-state"]):
            intf_data = reply_dict["data"]["interfaces-state"]["interface"]
            admin_status = intf_data.get("admin-status")
            oper_status = intf_data.get("oper-status")
            if admin_status == "up" and oper_status == "up":
                return f"Interface {loopback_name} is enabled (checked by Netconf)"
            elif admin_status == "down" and oper_status == "down":
                return f"Interface {loopback_name} is disabled (checked by Netconf)"
        else:
            return f"No Interface {loopback_name} (checked by Netconf)"
    except:
        return f"No Interface {loopback_name} (checked by Netconf)"
    finally:
        m.close_session()
