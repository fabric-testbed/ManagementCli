import json
import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .util import CText


cout = CText()

class NSOClient():
    def __init__(self, url, user, pwd):
        self._user = user
        self._pwd = pwd
        self._url = url

    def _get(self, ep):
        hdr = {"Accept": "application/yang-data+json"}
        url = f"{self._url}/{ep}"
        try:
            ret = requests.get(url, auth=(self._user, self._pwd), headers=hdr, verify=False)
            if not ret.text:
                return (dict(), ret.status_code)
            return (ret.json(), ret.status_code)
        except Exception as e:
            cout.error(f"GET: {e}")
            raise e

    def _patch(self, ep, data=None):
        hdr = {"Accept": "application/yang-data+json",
               "Content-type": "application/yang-data+json"}
        url = f"{self._url}/{ep}"
        try:
            ret = requests.patch(url, auth=(self._user, self._pwd), headers=hdr,
                                 data=data, verify=False)
            if not ret.text:
                return (dict(), ret.status_code)
            return (ret.json(), ret.status_code)
        except Exception as e:
            cout.error(f"PATCH: {e}")
            raise e

    def _post(self, ep, data=None):
        hdr = {"Accept": "application/yang-data+json",
               "Content-type": "application/yang-data+json"}
        url = f"{self._url}/{ep}"
        try:
            ret = requests.post(url, auth=(self._user, self._pwd), headers=hdr,
                                data=data, verify=False)
            if not ret.text:
                return (dict(), ret.status_code)
            return (ret.json(), ret.status_code)
        except Exception as e:
            cout.error(f"POST: {e}")
            raise e

    def _delete(self, ep, data=None):
        hdr = {"Accept": "application/yang-data+json",
               "Content-type": "application/yang-data+json"}
        url = f"{self._url}/{ep}"
        try:
            ret = requests.delete(url, auth=(self._user, self._pwd), headers=hdr,
                                  data=data, verify=False)
            if not ret.text:
                return (dict(), ret.status_code)
            return (ret.json(), ret.status_code)
        except Exception as e:
            cout.error(f"DELETE: {e}")
            raise e

    def devices(self):
        base = "tailf-ncs:devices/device"
        params = "fields=name;address;description;platform"
        ep = f"{base}?{params}"
        return self._get(ep)

    def config(self, dev):
        ep = f"tailf-ncs:devices/device={dev}/config"
        return self._get(ep)

    def packages(self):
        return self._get("tailf-ncs:packages")

    def services(self, service, name=None):
        ep = "tailf-ncs:services"
        if service:
            if name:
                return self._get(f"{ep}/{service}:{service}={name}")
            else:
                return self._get(f"{ep}/{service}:{service}")
        else:
            return self._get(ep)

    def create_service(self, s):
        ep = "tailf-ncs:services"
        data = json.dumps(s.json())
        return self._patch(ep, data)

    def delete_service(self, service, name=None):
        ep = "tailf-ncs:services"
        if service:
            if name:
                return self._delete(f"{ep}/{service}:{service}={name}")
            else:
                return self._delete(f"{ep}/{service}:{service}")
        return self._delete(ep)

    def sync(self, device, action):
        ep = f"tailf-ncs:devices/device={device}/{action}"
        return self._post(ep)

