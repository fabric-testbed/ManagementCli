import json
from time import time_ns


IDIPA_SERVICES=["l2ptp", "l2sts"]

class Endpoint():
    def __init__(self, ep):
        if not ep:
            return
        self.device = ep.get("device", None)
        self.port = ep.get("port", None)
        self.ero = ep.get("ero", None)
        self.bw = ep.get("bandwidth", None)
        self.ovlan = ep.get("outer_vlan", None)
        self.ivlan = ep.get("inner_vlan", None)
        self.bsize = ep.get("burst_size", None)
        self.addr_v4 = ep.get("address-v4", None)
        self.mask_v4 = ep.get("netmask-v4", None)
        self.addr_v6 = ep.get("address-v6", None)
        self.mask_v6 = ep.get("netmask-v6", None)
        self.gw_mac = ep.get("gateway-mac-address", None)

        if not self.device:
            raise Exception("No device specified for Endpoint")
        if not self.port:
            raise Exception("No port specified for Endpoint")

    def json_iface(self, device=True):
        ret = {
            "interface": {
                "type": self.port.split()[0],
                "id": self.port.split()[1]
            }
        }
        if device:
            ret["device"] = self.device
        iface = ret["interface"]
        if self.ovlan:
            iface["outervlan"] = self.ovlan
        if self.ivlan:
            iface["innervlan"] = self.ivlan
        if self.bw:
            qos = {"bandwidth": self.bw}
            if self.bsize:
                qos["burst-size"] = self.bsize
            iface.update(qos)
        return ret

    def json_ero(self):
        ret = {"hop": list()}
        if not self.ero:
            return ret
        idx = 1
        for hop in self.ero:
            h = {"address": hop,
                 "index": idx}
            ret["hop"].append(h)
            idx += 1
        return ret

class NSOService():
    def __init__(self, name=None, epa=None, epz=None):
        if name:
            self.name = name
        else:
            now = int(str(time_ns())[-6:])
            self.name = f"fabric-{self.service_str}-{now}"
        # XXX we will need to handle a list of EPs for some services, e.g. l2sts
        self.epa = Endpoint(epa)
        self.epz = Endpoint(epz)

    def __str__(self):
        return json.dumps(self.json())

    def _json_delete(self):
        ret = {
            "tailf-ncs:services": {
                self.service_id: [
                    {
                        "name": self.name
                    }
                ]
            }
        }
        return ret

class idipa(NSOService):
    service_str = "idipa"
    service_id = "idipa:idipa"

    def __init__(self, service=None, name=None):
        self.service = service
        self.name = name

    def json(self, delete=False):
        if delete:
            return self._json_delete()
        ret = {
            "tailf-ncs:services": {
                "idipa:idipa": [
                    {
                        "group": {
                            "service": self.service
                        },
                        "name": self.name
                    }
                ]
            }
        }
        return ret

class l2ptp(NSOService):
    service_str = "l2ptp"
    service_id = "l2ptp:l2ptp"

    def json(self, delete=False):
        if delete:
            return self._json_delete()

        l2ptp = {
            "name": self.name,
            "stp-a": self.epa.json_iface(),
            "stp-z": self.epz.json_iface()
        }

        if self.epa.ero:
            a2z = {"ero-a2z": self.epa.json_ero()}
            l2ptp.update(a2z)

        if self.epz.ero:
            z2a = {"ero-z2a": self.epz.json_ero()}
            l2ptp.update(z2a)

        ret = {
            "tailf-ncs:services": {
                self.service_id: [l2ptp]
            }
        }
        return ret

class l2sts(NSOService):
    service_str = "l2sts"
    service_id = "l2sts:l2sts"

    def json(self, delete=False):
        if delete:
            return self._json_delete()

        l2sts = {
            "name": self.name,
            "site-a": self.epa.json_iface(),
            "site-z": self.epz.json_iface()
        }

        if self.epa.ero:
            a2z = {"ero-a2z": self.epa.json_ero()}
            l2sts.update(a2z)

        if self.epz.ero:
            z2a = {"ero-z2a": self.epz.json_ero()}
            l2sts.update(z2a)

        ret = {
            "tailf-ncs:services": {
                self.service_id: [l2sts]
            }
        }
        return ret

class l2bridge(NSOService):
    service_str = "l2bridge"
    service_id = "l2bridge:l2bridge"

    def json(self, delete=False):
        if delete:
            return self._json_delete()

        l2bridge = {
            "name": self.name,
            "device": self.epa.device,
            "interface": [
                self.epa.json_iface(device=False),
                self.epz.json_iface(device=False)
            ]
        }

        ret = {
            "tailf-ncs:services": {
                self.service_id: [l2bridge]
            }
        }
        return ret

class l3rt(NSOService):
    service_str = "l3rt"
    service_id = "l3rt:l3rt"

    def json(self, delete=False):
        if delete:
            return self._json_delete()

        l3rt = {
            "name": self.name,
            "device": self.epa.device,
            "gateway-mac-address": self.epa.gw_mac,
            "interface": [
                self.epa.json_iface(device=False)["interface"]
            ]
        }

        if self.epa.addr_v4 and self.epa.mask_v4:
            v4 = {
                "gateway-ipv4": {
                    "address": self.epa.addr_v4,
                    "netmask": self.epa.mask_v4
                }
            }
            l3rt.update(v4)

        if self.epa.addr_v6 and self.epa.mask_v6:
            v6 = {
                "gateway-ipv6": {
                    "address": self.epa.addr_v6,
                    "netmask": self.epa.mask_v6
                }
            }
            l3rt.update(v6)

        ret = {
            "tailf-ncs:services": {
                self.service_id: [l3rt]
            }
        }
        return ret

class portmirror(NSOService):
    service_str = "port-mirror"
    service_id = "port-mirror:port-mirror"

    def json(self, delete=False):
        if delete:
            return self._json_delete()

        pm = {
            "name": self.name,
            "device": self.epa.device,
            "from-interface": self.epa.json_iface(device=False)["interface"],
            "to-interface": self.epz.json_iface(device=False)["interface"]
        }

        ret = {
            "tailf-ncs:services": {
                self.service_id: [pm]
            }
        }
        return ret
