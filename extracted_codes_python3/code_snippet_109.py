#!/usr/bin/env python3

"""
Crappy Network Interface

Very minimal Container Network Interface plugin

Command notes:
    ADD - creates only, no modification supported
    CHECK - unimplemented (not required by spec)
    DEL - implemented
    VERSIONS - implemented

Notes:
    * IPv4 only
    * NAT, if desired, must be managed manually
    * All plugins in one! Does not delegate to plugins
    * full of non-compliant race conditions
    * portmap and tuning not supported

Todo (maybe?):
    * plugins should be split out
    * minimal error handling

Required parameters (CNI spec):
    CNI_COMMAND
    CNI_CONTAINERID
    CNI_IFNAME
    CNI_NETNS -- Required for ADD, not for DEL

We ignore the following parameters:
    CNI_ARGS
    CNI_PATH
"""

from abc import ABC, abstractmethod
import ipaddress
import json
import os
import platform
from random import randint
import re
import subprocess
import sys



###############
# Global var(s)
###############

# Supported versions
# Pretty sure this plugin doesn"t actually support all these versions
VERSIONS_JSON = """
{
    "cniVersion": "0.4.0",
    "supportedVersions": [
        "0.3.1", "0.4.0", "1.0.0"
    ]
}
"""

NETNS_PATH = "/var/run/netns/"


#########
# Classes
#########

class CNIConfig:
    """
    Methods for reading CNI config values

    Probably should read this from /etc/cni/etc.d and parse the plugin stdinput
    separately

    Reusing class for ADD (which seems like it should match /etc/cni/etc.d
    config?) and DEL (which is passed a different structure)

    prevResult should really be handled as a subclass/separate object
    """

    def __init__(self, stdinput, request):
        self.stdinput = stdinput
        self.request = request
        self.config = self.__read_input(stdinput)
        self.cni_version = CNIConfig.read_cni_version()

        if self.request.command == "ADD":
            try:
                # Hardcoded to assume one plugin (host-local), probably bad
                self.bridge = self.config["bridge"]
                self.subnet = self.config["ipam"]["subnet"]
                self.gateway = self.config["ipam"]["gateway"]
            except:
                return_error(7, "Bad input",
                        "Input missing required ADD parameters")
        else:
            self.subnet = None
            self.gateway = None
            self.bridge = None

        if "prevResult" in self.config.keys() and self.request.command == "ADD":
            # Probably not compliant
            try:
                self.prev_result = self.config["prevResult"]
            except:
                if self.request.command == "DEL":
                    return_error(6, "Interface missing",
                        "Cannot read interface field in prevResult")

        elif "prevResult" not in self.config and self.request.command == "DEL":
            # requires prevResult
            return_error(6, "prevResult missing in input",
                   "prevResult is not in input json")

        elif "prevResult" in self.config:
            # this shouldn't happen but ok
            self.prev_result = self.config["prevResult"]
        else:
            self.prev_result = None


    @staticmethod
    def read_cni_version():
        """
        Read CNI version json to get default
        """
        versions = json.loads(VERSIONS_JSON)
        return versions["cniVersion"]


    def __read_input(self, stdinput):
        """
        Parse data from stdin
        """
        try:
            input_config = json.loads(stdinput)
            if input_config is None:
                return_error(5, "Invalid input JSON", "Cannot parse STDIN")
                return 5
        except:
            return_error(5, "Invalid input JSON", "Cannot parse STDIN")
            return 5
        else:
            return input_config



class CNIRequest:
    """
    Interface for CNI environment variables

    Supported/required vars:
        CNI_COMMAND
        CNI_CONTAINERID
        CNI_IFNAME -- harcoded as "eth0"
        CNI_NETNS -- FreeBSD doesn"t use named network isolation domains (?)

    We ignore the following parameters:
        CNI_ARGS
        CNI_PATH -- using /opt/cni/bin
    """

    env_vars = ["CNI_COMMAND", "CNI_CONTAINERID", "CNI_IFNAME", "CNI_NETNS"]
    verbs = ["ADD", "DEL", "CHECK", "VERSION"]

    def __init__(self):
        self.noop = CNIRequest.get_noop()
        for evar in CNIRequest.env_vars:
            if evar == "CNI_COMMAND":
                self.command = self.__verb()
            elif evar == "CNI_CONTAINERID":
                self.container_id = self.__read_var(evar)
            elif evar == "CNI_IFNAME":
                self.if_name = self.__read_var(evar)
            elif evar == "CNI_NETNS":
                self.netns = self.__read_var(evar)


    def __verb(self):
        verb = os.environ.get("CNI_COMMAND")
        if verb is None or verb not in CNIRequest.verbs:
            return_error(4, "Invalid CNI_COMMAND",
                "CNI_COMMAND must be one of " + ", ".join(CNIRequest.verbs))
            return 4
        return verb


    def __read_var(self, evar):
        value = os.environ.get(evar)
        # Sloppy way of handling sometimes-required params
        if self.command == "DEL" and evar == "CNI_NETNS" and value is None:
            # Not actually required for DEL
            return None

        if value is None:
            # Required for ADD and CHECK
            return_error(4, evar + " invalid", evar + " parameter invalid")
            return 4
        return value


    @staticmethod
    def get_noop():
        """
        If True, do not execute ifconfig/ip commands
        """

        val = os.environ.get("NOOP")
        if val in ("true", "True"):
            return True

        return False


class NetIf(ABC):
    """
    Interface for OS-level network interface configuration

    We have 3 different network devices to track:
    1. The bridge - on the host
    2. The virtual interface - seen from host side
    3. The container interface - seen from inside the container

    The LinkDevice subclass tracks these so we can just say something like
    "netif.bridge_if.device" or "netif.virtual_if.mac"
    """

    def __init__(self, cni, request):
        self.cni = cni
        self.request = request
        self.bridge_if = self.LinkDevice(self.cni.bridge)
        self.container_if = self.LinkDevice(self.request.if_name, None, None,
                NETNS_PATH + request.container_id)
        self.virtual_if = self.LinkDevice()


    class LinkDevice():
        """
        Embedded subclass, helps track the basics for multiple devices
        """
        def __init__(self, device=None, mac=None, ip=None, sandbox=None):
            self.device = device
            self.mac = mac
            self.ip = ip
            self.sandbox = sandbox


    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def allocate(self):
        pass

    @abstractmethod
    def read_mac_addr(request, device):
        pass

    @abstractmethod
    def new_ip(self):
        pass

    @staticmethod
    def gen_mac_addr():
        """
        Generate random MAC address
        """

        hexes = [ 0x01, 0x02, 0x03,
                randint(0x00, 0xff),
                randint(0x00, 0xff),
                randint(0x00, 0xff) ]
        return ":".join(f"{n:02X}" for n in hexes)


    @staticmethod
    def fix_netmask(octet_mask):
        """
        Convert xxx.xxx.xxx.xxx mask to /xx
        ipaddress module only return octet format
        """

        cidr = sum([bin(int(octet)).count("1") for octet in octet_mask.split(".")])
        return cidr


    @staticmethod
    def create_netif(cni, request):
        """
        Select NetIf implementation based on OS
        """
        osname = platform.system()
        if osname == "Linux":
            return LinuxNetIf(cni, request)

        if osname == "FreeBSD":
            return FreeBSDNetIf(cni, request)

        return_error(100, "OS unsupported", osname + " is not supported")
        return None



class FreeBSDNetIf(NetIf):
    """
    NetIf implementation for FreeBSD systems

    Not fully implemented or tested
    """

    # Prefix for virt network device
    interface_type = "tap"

    def __init__(self, cni, request):
        super().__init__(cni, request)
        self.bridge_if.mac = FreeBSDNetIf.read_mac_addr(self.request, self.bridge_if.device)


    def create(self):
        """
        Create the tap network device

        No error checking here

        Note that these commands are idempotent on FreeBSD;
        even if the device configurations already exist, as long as the
        configuration requests match, they will return true
        """
        self.allocate()
        self.new_ip()
        self.virtual_if.mac = NetIf.gen_mac_addr()

        if not self.request.noop:
            try:
                bridge = self.bridge_if.device
                device = self.virtual_if.device
                mac = self.virtual_if.mac
                os.system(f'ifconfig {device} create')
                os.system(f'ifconfig {device} link {mac}')
                os.system(f'ifconfig {bridge} addm {device}')
                os.system(f'ifconfig {device} up')
            except:
                return_error(11, "Failed to create device",
                        "Failed to create network device " + device)


    def allocate(self):
        """
        Choose random suffix for virtual device
        """

        ifnum = randint(0x00, 0xffffff)
        self.virtual_if.device = FreeBSDNetIf.interface_type + f'{ifnum:02x}'


    def delete(self):
        """
        Delete the virtual network device

        No error checking here

        Note that these commands are idempotent on FreeBSD;
        if the requested interface does not exist for any reason,
        they will still return true
        """

        if not self.request.noop:
            try:
                os.system("ifconfig " + self.virtual_if.device + " destroy")
            except:
                return_error(7, "Failed to delete device",
                        "Failed to delete network device")

        return True


    @staticmethod
    def read_mac_addr(request, device):
        """
        Parse device MAC address from ifconfig output
        """
        if request.noop:
            return "aa:aa:aa:aa:aa:aa"

        try:
            ifconfig = subprocess.run(["ifconfig", device],
                    stdout=subprocess.PIPE, check=False)
            ifout = ifconfig.stdout.decode("UTF-8")

            ematch = re.compile(r"ether\s+(..:..:..:..:..:..)")
            return ematch.search(ifout)
        except:
            return None


    def new_ip(self):
        """
        Hardcoded stub for now. Should check something stateful for unused IPs
        in subnet range

        Todo: check for free IPs
        """

        # hardcode for now
        ipaddr = "172.16.0.12"
        subnet = self.cni.subnet
        subnet_cidr = ipaddress.ip_network(subnet)
        netmask = str(subnet_cidr.netmask)
        cidr_nm = NetIf.fix_netmask(netmask)
        cidr = f'{ipaddr}/{cidr_nm}'
        self.container_if.ip = cidr



class LinuxNetIf(NetIf):
    """
    NetIf implementation for Linux systems
    """

    # Prefix for virt network device
    interface_type = "veth"

    def __init__(self, cni, request):
        super().__init__(cni, request)
        self.bridge_if.mac = LinuxNetIf.read_mac_addr(self.request, self.bridge_if.device)


    def create(self):
        """
        Create the virtual network device

        No error checking here
        """
        self.allocate()
        self.new_ip()
        self.container_if.mac = NetIf.gen_mac_addr()

        if self.request.noop:
            return True

        try:
            bridge_device = self.bridge_if.device
            virtual_device = self.virtual_if.device
            container_device = self.container_if.device
            container_id = self.request.container_id
            container_ip = self.container_if.ip
            gateway = self.cni.gateway
            netns = self.request.netns

            os.system(f'ip link add {container_device} type veth \
                    peer name {virtual_device}')
            os.system(f'ip link set dev {virtual_device} up')
            os.system(f'ip link set dev {virtual_device} \
                    master {bridge_device}')
            os.system(f'ln -sfT {netns} /var/run/netns/{container_id}')
            os.system(f'ip netns add {container_id}')
            os.system(f'ip link set {container_device} \
                    netns {container_id}')
            os.system(f'ip netns exec {container_id} ip link \
                    set {container_device} up')
            os.system(f'ip netns exec {container_id} ip addr add \
                    {container_ip} dev {container_device}')
            os.system(f'ip netns exec {container_id} ip route \
                    add {gateway} dev {container_device}')
            os.system(f'ip netns exec {container_id} ip route \
                    add default via {gateway} dev {container_device}')

            self.container_if.mac = self.read_netns_mac_addr()
            self.virtual_if.mac = \
                    LinuxNetIf.read_mac_addr(self.request, \
                    self.virtual_if.device)
        except:
            return_error(11, "Failed to create device",
                    "Failed to create network device " + virtual_device)


    def allocate(self):
        """
        Choose random suffix for virtual device
        """

        ifnum = randint(0x00, 0xffffff)
        self.virtual_if.device = LinuxNetIf.interface_type + f'{ifnum:02x}'


    def delete(self):
        """
        Delete the virtual network device

        No error checking here
        """

        self.update_virtual_if()

        if self.request.noop:
            return True

        device = self.virtual_if.device
        container = self.request.container_id

        try:
            os.system(f'ip link set dev {device} down')
            os.system(f'ip link delete {device}')
            os.system(f'ip netns delete {container}')
        except:
            return_error(7, "Failed to delete device",
                    "Failed to delete network device " + device)
        return True


    def update_virtual_if(self):
        """
        Fill in self.virtual_if structure
        """
        try:
            for iface in self.cni.prev_result["interfaces"]:
                if iface["name"].startswith(LinuxNetIf.interface_type):
                    self.virtual_if.device = iface["name"]
        except:
            return_error(7, "Failed to delete device",
                    "Failed to delete network device")


    @staticmethod
    def read_mac_addr(request, device):
        """
        Parse device MAC address from ifconfig output
        """
        if request.noop:
            return "aa:bb:cc:dd:dd:dd"

        try:
            ifconfig = subprocess.run(["ip", "-br", "link", "show", device],
                    stdout=subprocess.PIPE, check=False)
            ifout = ifconfig.stdout.decode("UTF-8")
            return ifout.split()[2]
        except:
            return 1


    def read_netns_mac_addr(self):
        """
        Parse device container mac address from ip output
        """
        if self.request.noop:
            return "aa:aa:aa:aa:aa:aa"

        try:
            container_id = self.request.container_id
            container_device = self.container_if.device
            ifconfig = subprocess.run(["ip", "netns", "exec", \
                    container_id, "ip", "-br", "link", "show", container_device],
                    stdout=subprocess.PIPE, check=False)
            ifout = ifconfig.stdout.decode("UTF-8")
            return ifout.split()[2]
        except:
            #return_error(11, "Failed to read mac addr device",
            #        "Failed to create network device")
            return None


    def new_ip(self):
        """
        Assign IP to the container interface

        Hardcoded stub for now. Should check something stateful for unused IPs
        in subnet range

        Todo: check for free IPs
        """

        # hardcode for now
        ipaddr = "172.16.0.123"
        subnet = self.cni.subnet
        subnet_cidr = ipaddress.ip_network(subnet)
        netmask = str(subnet_cidr.netmask)
        cidr_nm = NetIf.fix_netmask(netmask)
        cidr = f'{ipaddr}/{cidr_nm}'
        self.container_if.ip = cidr
        return cidr



class AddResult:
    """
    Holds structure for ADD command results
    """

    def __init__(self, cni, request, netif):
        self.cni_version = CNIConfig.read_cni_version()
        self.cni = cni
        self.request = request
        self.netif = netif

        self.interfaces = []

        self.ips = [
                {
                    "version": "4",
                    "gateway": self.cni.gateway,
                    "interface": 2,
                }
        ]


    def set_if_result(self, device):
        """
        Fill missing device class vars
        """
        result = {}

        #if device.ip is not None:
        #    result["ip"] = device.ip

        if device.mac is not None:
            result["mac"] = device.mac

        if device.device is not None:
            result["name"] = device.device

        if device.sandbox is not None:
            result["sandbox"] = device.sandbox

        self.interfaces.append(result)


    def json_output(self):
        """
        ADD result CNI output
        """
        self.set_if_result(self.netif.bridge_if)
        self.set_if_result(self.netif.virtual_if)
        # container interface: 2
        self.set_if_result(self.netif.container_if)
        self.ips[0]["address"] = self.netif.container_if.ip
        if "dns" in self.cni.config:
            dns = self.cni.config["dns"]
        else:
            dns = {}

        result = {
                "cniVersion": self.cni_version,
                "interfaces": self.interfaces,
                "ips": self.ips,
                "dns": dns
                }
        return json.dumps(result)



################
# Global methods (for now?)
################

def command_add(cni, request):
    """
    CNI ADD verb
    """

    netif = NetIf.create_netif(cni, request)
    result = AddResult(cni, request, netif)
    host_local_add(netif)

    print(result.json_output())
    sys.exit(0)


def command_del(cni, request):
    """
    CNI DEL verb
    """

    # Should only return 0 as errors shouldn't bubble up but *shrug*
    netif = NetIf.create_netif(cni, request)
    code = host_local_del(netif)
    if code:
        sys.exit(0)
    else:
        sys.exit(1)


def command_check():
    """
    CNI CHECK verb

    added in CNI v0.4

    required for CNI v1.0.0, at least for internal use?
    """

    print("Not implemented; CHECK disabled")
    sys.exit(0)


def command_version():
    """
    CNI VERSION verb
    """

    print(VERSIONS_JSON)
    sys.exit(0)


def host_local_add(netif):
    """
    Create the interface
    """

    netif.create()


def host_local_del(netif):
    """
    Delete the interface
    """

    return netif.delete()


def return_error(code, msg, details):
    """
    Return the error message in format as shown at
    https://github.com/containernetworking/cni/blob/main/SPEC.md#Error

    This method makes no checks on its args
    """

    error_msg = {"cniVersion": CNIConfig.read_cni_version(),
            "code": code, "msg": msg, "details": details}
    return_msg = json.dumps(error_msg)

    print(return_msg, file=sys.stderr)
    raise SystemExit(code)



def main():
    """
    Main
    """
    request = CNIRequest()

    input_json = "".join(sys.stdin.readlines())
    config = CNIConfig(input_json, request)

    if request.command == "ADD":
        command_add(config, request)
    elif request.command == "DEL":
        command_del(config, request)
    elif request.command == "CHECK":
        command_check()
    elif request.command == "VERSION":
        command_version()


if __name__ == "__main__":
    main()
