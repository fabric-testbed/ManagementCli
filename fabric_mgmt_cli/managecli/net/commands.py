#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 FABRIC Testbed
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
# Author: Komal Thareja (kthare10@renci.org)
# Author: Ezra Kissel (kissel@es.net)
import os
import click
import json

from fabric_mgmt_cli.managecli.config_processor import ConfigProcessor
from fabric_mgmt_cli.managecli.net import services as NSOServices
from .nso import NSOClient
from .services import idipa, IDIPA_SERVICES
from .resources import Inventory

class NetCommand:
    PATH = os.environ.get('FABRIC_MGMT_CLI_CONFIG_PATH', './config.yml')

    def __init__(self, dry_run=False):
        self.cfg = ConfigProcessor(path=self.PATH)
        self.cfg.process()
        self.nso = NSOClient(self.cfg.get_net_url(),
                             self.cfg.get_net_username(),
                             self.cfg.get_net_password())
        self._res = None
        self._code = None
        self._dry_run = dry_run

    def sync_device(self, device, action):
        try:
            self._res, self._code = self.nso.sync(device, action)
        except:
            pass

    def get_devices(self):
        try:
            self._res, self._code = self.nso.devices()
        except:
            pass

    def get_packages(self):
        try:
            self._res, self._code = self.nso.packages()
        except:
            pass

    def get_services(self, service, name):
        try:
            self._res, self._code = self.nso.services(service, name)
        except:
            pass

    def get_config(self, device):
        try:
            self._res, self._code = self.nso.config(device)
        except:
            pass

    def create_service(self, service):
        if self._dry_run:
            self._res, self._code = service.json(), 0
            return
        try:
            self._res, self._code = self.nso.create_service(service)
        except:
            pass

    def delete_service(self, service, name):
        self._res, self._code = self.nso.delete_service(service, name)

    def print_result(self, txt=None, verbose=False):
        if self._res == None:
            return
        if txt:
            print (txt, end=f" - Response ({self._code}): ")
        if verbose:
            formatted_json = json.dumps(self._res, sort_keys=True, indent=4)
            try:
                from pygments import highlight, lexers, formatters
                colorful_json = highlight(formatted_json, lexers.JsonLexer(),
                                          formatters.TerminalFormatter())
                print (colorful_json)
            except:
                print (formatted_json)
            return

        new = dict()
        for k,v in self._res.items():
            if isinstance(v, dict):
                for l,w in v.items():
                    if not isinstance(w, list):
                        continue
                    for d in w:
                        if isinstance(d, dict) and "name" in d:
                            new[str(d['name'])] = d
                            d['opts'] = l
            elif isinstance(v, list):
                for d in v:
                    if isinstance(d, dict) and "name" in d:
                        new[str(d['name'])] = d

        for k,v in new.items():
            if "opts" in v:
                disp = f"{k: <30} | {v['opts']: <60} |"
            elif "description" in v:
                disp = f"{k: <30} | {v['description']: <60} |"
            else:
                disp = f"{k}"
            print (disp)

@click.group()
@click.pass_context
def net(ctx):
    """ Dataplane network management
    """
    config = os.getenv('FABRIC_MGMT_CLI_CONFIG_PATH')
    if config is None or config == "":
        ctx.fail('FABRIC_MGMT_CLI_CONFIG_PATH is not set')
    return

@click.group()
@click.option('-v', '--verbose', is_flag=True)
@click.pass_context
def show(ctx, verbose):
    """ Subgroup for network information commands
    """
    ctx.ensure_object(dict)
    ctx.obj['VERBOSE'] = verbose
    pass

@net.command()
@click.argument('action', nargs=1)
@click.option('--device', default=None, help='Device to sync', required=True)
@click.option('-v', '--verbose', is_flag=True)
@click.pass_context
def sync(ctx, verbose, device,  action):
    """ Control NSO device synchronization
    """
    sync_actions = ['sync-from', 'check-sync']
    if action not in sync_actions:
        print (f"Unknown action: {action}")
        return
    net_cmd = NetCommand()
    net_cmd.sync_device(device, action)
    net_cmd.print_result(verbose=verbose)

@net.command()
@click.option('--inventory', default=None, help='Inventory file', required=True)
@click.option('--epa', default=None, help='Endpoint A', required=True)
@click.option('--epz', default=None, help='Endpoint Z', required=False)
@click.option('--service', default=None, help='Service', required=True)
@click.option('--name', default=None, help='Service name', required=False)
@click.option('--dry-run', is_flag=True, help='Perform a dry run without configuring devices')
@click.pass_context
def create(ctx, inventory, epa, epz, service, name, dry_run):
    """ Create a new network service
    """
    try:
        inv = Inventory(inventory)
        a = inv.resolve_resource(epa)
        if service != "l3rt":
            z = inv.resolve_resource(epz)
        else:
            z = None
    except Exception as e:
        print (f"Error in create: {e}")
        return

    cls = getattr(NSOServices, service, None)
    if not cls:
        print (f"Unknown service {service}")
        return

    # name is auto-generated if None
    s = cls(name=name, epa=a, epz=z)
    net_cmd = NetCommand(dry_run)
    if service in IDIPA_SERVICES:
        ids = idipa(service, s.name)
        net_cmd.create_service(ids)
    net_cmd.create_service(s)
    net_cmd.print_result(f"Created service {service}: {s.name}", True)

@net.command()
@click.option('--service', default=None, help='Service', required=True)
@click.option('--name', default=None, help='Service name to delete', required=True)
@click.pass_context
def delete(ctx, service, name):
    """ Delete an existing network service by name
    """
    cls = getattr(NSOServices, service, None)
    if not cls:
        print (f"Unknown service {service}")
        return

    s = cls(name=name)
    net_cmd = NetCommand()
    if service in IDIPA_SERVICES:
        ids = idipa(service, s.name)
        net_cmd.delete_service(ids.service_str, name)
    net_cmd.delete_service(s.service_str, name)
    net_cmd.print_result(f"Delete {service} service: {s.name}", True)

@show.command()
@click.pass_context
def devices(ctx):
    """ Show devices known to network controller
    """
    net_cmd = NetCommand()
    net_cmd.get_devices()
    net_cmd.print_result(verbose=ctx.obj['VERBOSE'])

@show.command()
@click.pass_context
def packages(ctx):
    """ Show packages known to network controller
    """
    net_cmd = NetCommand()
    net_cmd.get_packages()
    net_cmd.print_result(verbose=ctx.obj['VERBOSE'])

@show.command()
@click.pass_context
@click.option('--service', default=None, help='Service', required=False)
@click.option('--name', default=None, help='Service name', required=False)
def services(ctx, service, name):
    """ Show services known to network controller
    """
    if name and not service:
        print ("Name requires specifying service option")
        return
    net_cmd = NetCommand()
    net_cmd.get_services(service, name)
    net_cmd.print_result(verbose=ctx.obj['VERBOSE'])

@show.command()
@click.option('--device', default=None, help='Device name', required=True)
@click.pass_context
def config(ctx, device):
    """ Show device configuration
    """
    net_cmd = NetCommand()
    net_cmd.get_config(device)
    net_cmd.print_result(verbose=True)

net.add_command(show)
