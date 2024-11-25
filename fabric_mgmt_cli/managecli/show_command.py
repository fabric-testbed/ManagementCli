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
import json
import re
import traceback
from typing import Tuple, List

from fabric_cf.actor.core.apis.abc_delegation import DelegationState
from fabric_cf.actor.core.common.constants import Constants
from fabric_cf.actor.core.kernel.reservation_states import ReservationStates, ReservationPendingStates
from fabric_cf.actor.core.kernel.slice_state_machine import SliceState
from fabric_cf.actor.core.manage.error import Error
from fabric_cf.actor.core.time.actor_clock import ActorClock
from fabric_cf.actor.core.util.id import ID
from fabric_cf.actor.core.util.utils import sliver_to_str
from fabric_mb.message_bus.messages.delegation_avro import DelegationAvro
from fabric_mb.message_bus.messages.lease_reservation_avro import LeaseReservationAvro
from fabric_mb.message_bus.messages.reservation_mng import ReservationMng
from fabric_mb.message_bus.messages.site_avro import SiteAvro
from fabric_mb.message_bus.messages.slice_avro import SliceAvro
from fim.graph.abc_property_graph import ABCPropertyGraph
from fim.slivers.attached_components import ComponentType
from fim.slivers.network_node import NodeSliver
from fim.slivers.network_service import NetworkServiceSliver

from fabric_mgmt_cli.managecli.command import Command


class ShowCommand(Command):
    def get_slices(self, *, actor_name: str, callback_topic: str, slice_id: str, slice_name: str, id_token: str,
                   email: str, states: str, format: str):
        try:
            slices, error = self.do_get_slices(actor_name=actor_name, callback_topic=callback_topic, slice_id=slice_id,
                                               slice_name=slice_name, id_token=id_token, email=email, states=states)
            if slices is not None and len(slices) > 0:
                self.__print_slices(slices=slices, format=format)
            else:
                print("Status: {}".format(error.get_status()))
        except Exception as e:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
            print("Exception occurred while processing get_slices {}".format(e))

    def parse_slice_ids_from_file(self, slice_id_file: str) -> list:
        """
        Reads slice IDs from a file and splits comma-separated values into individual slice IDs.

        Args:
            slice_id_file (str): Path to the file containing slice IDs.

        Returns:
            list: A list of slice IDs.
        """
        slice_ids = []
        try:
            with open(slice_id_file, "r") as f:
                for line in f:
                    # Split comma-separated slice IDs and strip whitespace
                    slice_ids.extend([slice_id.strip() for slice_id in line.split(",") if slice_id.strip()])
        except Exception as e:
            print(f"Error reading slice ID file: {e}")
        return slice_ids

    def get_reservations(self, *, actor_name: str, callback_topic: str, slice_id: str, rid: str,
                         states: str, id_token: str, email: str, site: str, type: str, format: str, fields: str,
                         include_ansible: bool, host: str, ip_subnet: str, slice_id_file: str, output_file: str):
        try:
            # Determine query input (slice_id, slice_id_file, or sliverid)
            if slice_id_file:
                slice_ids = self.parse_slice_ids_from_file(slice_id_file)
                if not slice_ids:
                    print(f"Error: No valid slice IDs found in {slice_id_file}")
                    return
            elif slice_id:
                # Use single slice ID if provided
                slice_ids = [slice_id]
            elif rid:
                # Use sliverid directly if no slice_id or slice_id_file is provided
                slice_ids = []  # Slice IDs not used when querying by sliver ID
            else:
                slice_ids = None

            # Prepare for output redirection
            output = []
            if slice_ids:
                # Query for each slice ID
                for sid in slice_ids:
                    try:
                        reservations, error = self.do_get_reservations(actor_name=actor_name,
                                                                       callback_topic=callback_topic,
                                                                       slice_id=sid, rid=None, states=states,
                                                                       id_token=id_token,
                                                                       email=email, site=site, type=type, host=host,
                                                                       ip_subnet=ip_subnet)
                        if reservations is not None and len(reservations) > 0:
                            result = self.__print_reservations(reservations=reservations, format=format, fields=fields,
                                                               include_ansible=include_ansible, return_as_string=True)
                            output.append(result)
                        else:
                            output.append(f"Slice ID: {sid}, Status: {error.get_status()}\n")
                    except Exception as e:
                        ex_str = traceback.format_exc()
                        self.logger.error(ex_str)
                        output.append(f"Slice ID: {sid}, Exception occurred: {e}\n")
            else:
                # Query using sliverid (rid)
                try:
                    reservations, error = self.do_get_reservations(actor_name=actor_name, callback_topic=callback_topic,
                                                                   slice_id=None, rid=rid, states=states,
                                                                   id_token=id_token,
                                                                   email=email, site=site, type=type, host=host,
                                                                   ip_subnet=ip_subnet)
                    if reservations is not None and len(reservations) > 0:
                        result = self.__print_reservations(reservations=reservations, format=format, fields=fields,
                                                           include_ansible=include_ansible, return_as_string=True)
                        output.append(result)
                    else:
                        output.append(f"Sliver ID: {rid}, Status: {error.get_status()}\n")
                except Exception as e:
                    ex_str = traceback.format_exc()
                    self.logger.error(ex_str)
                    output.append(f"Sliver ID: {rid}, Exception occurred: {e}\n")

            # Redirect output to a file if specified
            if output_file:
                try:
                    with open(output_file, 'w') as f:
                        f.writelines(output)
                    print(f"Output written to {output_file}")
                except Exception as e:
                    self.logger.error(f"Error writing to output file: {e}")
                    print(f"Error writing to output file: {e}")
            else:
                # Print output to the console
                for line in output:
                    print(line)
        except Exception as e:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
            print(f"Exception occurred while processing get_reservations: {e}")

    def get_delegations(self, *, actor_name: str, callback_topic: str, slice_id: str, did: str, states: str,
                        id_token: str, format: str):
        try:
            delegations, error = self.do_get_delegations(actor_name=actor_name, callback_topic=callback_topic,
                                                         slice_id=slice_id, did=did, states=states, id_token=id_token)
            if delegations is not None and len(delegations) > 0:
                self.__print_delegations(delegations=delegations, format=format)
            else:
                print("Status: {}".format(error.get_status()))
        except Exception as e:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
            print("Exception occurred while processing get_delegations {}".format(e))

    def do_get_slices(self, *, actor_name: str, callback_topic: str, slice_id: str = None, slice_name: str = None,
                      id_token: str = None, email: str = None, states: str = None, projectid: str = None) -> Tuple[
        List[SliceAvro] or None, Error]:
        actor = self.get_actor(actor_name=actor_name)

        if actor is None:
            raise Exception("Invalid arguments actor {} not found".format(actor_name))
        try:
            actor.prepare(callback_topic=callback_topic)
            sid = ID(uid=slice_id) if slice_id is not None else None
            slice_states = None
            if states is not None:
                states_list = states.split(",")
                for x in states_list:
                    if slice_states is None:
                        slice_states = []
                    x = x.strip()
                    slice_states.append(SliceState.translate(state_name=x).value)

            result = actor.get_slices(slice_id=sid, slice_name=slice_name, email=email, states=slice_states,
                                      project=projectid)
            return result, actor.get_last_error()
        except Exception:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
        return None, actor.get_last_error()

    def do_get_reservations(self, *, actor_name: str, callback_topic: str, slice_id: str = None, rid: str = None,
                            states: str = None, id_token: str = None, email: str = None, site: str = None,
                            type: str = None, host: str = None, ip_subnet: str = None) -> Tuple[List[ReservationMng] or None, Error]:
        actor = self.get_actor(actor_name=actor_name)

        if actor is None:
            raise Exception("Invalid arguments actor {} not found".format(actor_name))
        try:
            actor.prepare(callback_topic=callback_topic)
            sid = ID(uid=slice_id) if slice_id is not None else None
            reservation_id = ID(uid=rid) if rid is not None else None
            reservation_states = None
            if states is not None:
                states_list = states.split(",")
                for x in states_list:
                    if reservation_states is None:
                        reservation_states = []
                    x = x.strip()
                    reservation_states.append(ReservationStates.translate(state_name=x).value)
            return actor.get_reservations(slice_id=sid, rid=reservation_id, states=reservation_states, email=email,
                                          site=site, type=type, host=host, ip_subnet=ip_subnet), actor.get_last_error()
        except Exception as e:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
        return None, actor.get_last_error()

    def do_get_delegations(self, *, actor_name: str, callback_topic: str, slice_id: str = None, did: str = None,
                           states: str = None, id_token: str = None) -> Tuple[List[DelegationAvro] or None, Error]:
        actor = self.get_actor(actor_name=actor_name)

        if actor is None:
            raise Exception("Invalid arguments actor {} not found".format(actor_name))
        try:
            actor.prepare(callback_topic=callback_topic)
            sid = None
            if slice_id is not None:
                sid = ID(uid=slice_id)
            delegation_states = None
            if states is not None:
                for x in states:
                    if delegation_states is None:
                        delegation_states = []
                    x = x.strip()
                    delegation_states.append(DelegationState.translate(state_name=x).value)
            return actor.get_delegations(delegation_id=did, slice_id=sid,
                                         states=delegation_states), actor.get_last_error()
        except Exception as e:
            self.logger.error(f"Exception occurred while fetching delegations: e {e}")
            self.logger.error(traceback.format_exc())
            traceback.print_exc()
        return None, actor.get_last_error()

    @staticmethod
    def __print_reservations_json(*, reservations: List[ReservationMng], fields: str, return_as_string: bool = False):
        """
        Print or return reservations in JSON format.

        Args:
            reservations (List[ReservationMng]): List of reservation objects.
            fields (str): Comma-separated list of fields to include.
            return_as_string (bool): If True, return the output as a string. Otherwise, print it.
        """
        res_list = []
        if fields is not None:
            field_list = fields.split(",")
        else:
            field_list = None

        for reservation in reservations:
            res_dict = {
                "sliver_id": reservation.reservation_id,
                "slice_id": reservation.slice_id,
            }
            if reservation.rtype is not None and (field_list is None or "type" in field_list):
                res_dict["type"] = reservation.rtype

            if reservation.rtype is not None and (field_list is None or "notices" in field_list):
                res_dict["notices"] = reservation.notices

            if reservation.start is not None and (field_list is None or "start" in field_list):
                res_dict["start"] = ShowCommand.time_string(milliseconds=reservation.start)

            if reservation.end is not None and (field_list is None or "end" in field_list):
                res_dict["end"] = ShowCommand.time_string(milliseconds=reservation.end)

            if reservation.requested_end is not None and (field_list is None or "requested_end" in field_list):
                res_dict["requested_end"] = ShowCommand.time_string(milliseconds=reservation.requested_end)

            if reservation.units is not None and (field_list is None or "units" in field_list):
                res_dict["units"] = reservation.units

            if reservation.state is not None and (field_list is None or "state" in field_list):
                res_dict["state"] = reservation.state

            if reservation.pending_state is not None and (field_list is None or "pending_state" in field_list):
                res_dict["pending_state"] = reservation.pending_state

            sliver = reservation.get_sliver()
            if sliver is not None and (field_list is None or "sliver" in field_list):
                res_dict["sliver"] = ABCPropertyGraph.sliver_to_dict(sliver)

            res_list.append(res_dict)

        json_output = json.dumps(res_list, indent=4)
        if return_as_string:
            return json_output
        print(json_output)

    def __print_reservations(self, reservations: List[ReservationMng], format: str, fields: str,
                             include_ansible: bool = False, return_as_string: bool = False):
        """
        Print or return reservations based on the specified format.

        Args:
            reservations (List[ReservationMng]): List of reservation objects.
            format (str): Output format ('text' or 'json').
            fields (str): Comma-separated list of fields to include.
            include_ansible (bool): Whether to include ansible commands (text format only).
            return_as_string (bool): If True, return the output as a string. Otherwise, print it.
        """
        if format == "text":
            result = []
            for r in reservations:
                output = self.__print_reservation(reservation=r, include_ansible=include_ansible, return_as_string=True)
                if return_as_string:
                    result.append(output)
                else:
                    print(output)
            if return_as_string:
                return "\n".join(result)
        else:
            return self.__print_reservations_json(reservations=reservations, fields=fields,
                                                  return_as_string=return_as_string)

    @staticmethod
    def __print_reservation(*, reservation: ReservationMng, include_ansible: bool, return_as_string: bool = False):
        """
        Print or return details of a single reservation.

        Args:
            reservation (ReservationMng): Reservation object to print.
            include_ansible (bool): Whether to include ansible commands.
            return_as_string (bool): If True, return the output as a string. Otherwise, print it.
        """
        output = []
        output.append("")
        output.append(f"Reservation ID: {reservation.reservation_id} Slice ID: {reservation.slice_id}")
        if reservation.rtype is not None or reservation.notices is not None:
            output.append(f"Resource Type: {reservation.rtype} Notices: {reservation.notices}")

        if reservation.start is not None or reservation.end is not None or reservation.requested_end is not None:
            output.append(f"Start: {ShowCommand.time_string(milliseconds=reservation.start)} "
                  f"End: {ShowCommand.time_string(milliseconds=reservation.end)} "
                  f"Requested End: {ShowCommand.time_string(milliseconds=reservation.requested_end)}")

        if reservation.units is not None or reservation.state is not None or reservation.pending_state is not None:
            output.append(f"Units: {reservation.units} State: {ReservationStates(reservation.state)} "
                  f"Pending State: {ReservationPendingStates(reservation.pending_state)}")

        if isinstance(reservation, LeaseReservationAvro) and reservation.redeem_processors is not None:
            output.append(f"Predecessors")
            for x in reservation.redeem_processors:
                output.append(x.get_reservation_id())

        sliver = reservation.get_sliver()
        if sliver is not None:
            output.append(f"Sliver: {sliver_to_str(sliver=sliver)}")

            if include_ansible and isinstance(sliver, NodeSliver):
                from fabric_mgmt_cli.managecli.kafka_processor import KafkaProcessorSingleton
                playbook_config = KafkaProcessorSingleton.get().get_playbook_config()
                location = playbook_config.get("location")
                inventory_path = playbook_config.get("inventory_location")

                output.append("")
                output.append("Ansible commands to attach the PCI devices:")
                output.append("")
                if sliver.attached_components_info is not None:
                    for component in sliver.attached_components_info.devices.values():
                        if component.get_type() == ComponentType.Storage:
                            continue
                        playbook = playbook_config.get(str(component.get_type()))
                        playbook_full_path = f"{location}/{playbook}"

                        if isinstance(component.labels.bdf, str):
                            pci_device_list = [component.labels.bdf]
                        else:
                            pci_device_list = component.labels.bdf

                        cmd = f"ansible-playbook -i {inventory_path} {playbook_full_path} --extra-vars " \
                              f"'worker_node_name={sliver.label_allocations.instance_parent} " \
                              f"device={reservation.reservation_id} operation=attach " \
                              f"kvmguest_name={sliver.label_allocations.instance} "

                        if component.get_type() == ComponentType.FPGA:
                            bdf = str(pci_device_list[0])
                            pattern = r'(\d+):(\d+):(\d+)\.(\d)'
                            matches = re.match(pattern, bdf)

                            host_vars = {
                                "domain": f"0x{matches[1]}",
                                "bus": f"0x{matches[2]}",
                                "slot": f"0x{matches[3]}"
                            }

                            for key, value in host_vars.items():
                                cmd += f"{key}={value} "
                            cmd += "'"
                            print()
                            print(cmd)
                            continue

                        # Grab the Mac addresses
                        interface_names = []
                        ns = None
                        if component.get_type() in [ComponentType.SmartNIC, ComponentType.SharedNIC]:
                            ns_name = list(component.network_service_info.network_services.keys())[0]
                            ns = component.network_service_info.network_services[ns_name]
                            interface_names = list(ns.interface_info.interfaces.keys())

                        idx = 0
                        for device in pci_device_list:
                            device_info = ""
                            device_char_arr = ShowCommand.__extract_device_addr_octets(device_address=device)
                            device = device.replace("0000:", "")

                            mac = None
                            if len(interface_names) > 0:
                                mac = ns.interface_info.interfaces[interface_names[idx]].label_allocations.mac.lower()
                            idx += 1

                            host_vars = {
                                "domain": device_char_arr[0],
                                "bus": device_char_arr[1],
                                "slot": device_char_arr[2],
                                "function": device_char_arr[3],
                                "bdf" : device
                            }
                            if mac is not None:
                                host_vars["mac"] = mac

                            for key, value in host_vars.items():
                                device_info += f"{key}={value} "
                            #cmd += "'"
                            output.append("")
                            output.append(f"{cmd} {device_info}'")
        result = "\n".join(output)
        if return_as_string:
            return result
        print(result)

    @staticmethod
    def __print_node_sliver(*, sliver: NodeSliver):
        if sliver.attached_components_info is not None:
            for c in sliver.attached_components_info.devices.items():
                print(c)

    @staticmethod
    def __print_ns_sliver(*, sliver: NetworkServiceSliver):
        if sliver.interface_info is not None:
            for c in sliver.interface_info.interfaces.values():
                print(c)

    @staticmethod
    def time_string(*, milliseconds):
        time_obj = ActorClock.from_milliseconds(milli_seconds=milliseconds)
        return time_obj.strftime(Constants.LEASE_TIME_FORMAT)

    @staticmethod
    def __print_slice(*, slice_object: SliceAvro):
        """
        Prints Slice Object
        """
        print("")
        print(f"Slice Name: {slice_object.get_slice_name()} Slice ID: {slice_object.get_slice_id()} "
              f"Project ID: {slice_object.get_project_id()} Project Name: {slice_object.get_project_name()} ")
        if slice_object.get_graph_id() is not None:
            print(f"Graph ID: {slice_object.get_graph_id()}")

        if slice_object.get_owner() is not None:
            print(f"Slice owner: {slice_object.get_owner()}")

        if slice_object.get_state() is not None:
            print(f"Slice state: {str(SliceState(slice_object.get_state()))}")

        if slice_object.get_lease_end() is not None:
            print(f"Lease time: {slice_object.get_lease_end()}")
        print("")

    @staticmethod
    def __print_slice_json(*, slices: List[SliceAvro]):
        """
        Prints Slice Object
        """
        slc_list = []
        for slice_object in slices:
            slc_dict = {'name': slice_object.get_slice_name(),
                        'slice_id': slice_object.get_slice_id(),
                        'project_id': slice_object.get_project_id(),
                        'project_name': slice_object.get_project_name(),
                        'graph_id': slice_object.get_graph_id(),
                        'owner': slice_object.get_owner().get_email(),
                        'state': str(SliceState(slice_object.get_state())),
                        'lease_start_time': str(slice_object.get_lease_start()),
                        'lease_end_time': str(slice_object.get_lease_end())
                        }
            slc_list.append(slc_dict)

        print(json.dumps(slc_list, indent=4))

    def __print_slices(self, slices: List[SliceAvro], format: str):
        if format == 'text':
            for s in slices:
                self.__print_slice(slice_object=s)
        else:
            self.__print_slice_json(slices=slices)

    @staticmethod
    def __print_delegation(*, dlg_object: DelegationAvro):
        """
        Prints the Delegation Object
        """
        print("")
        print("Delegation ID: {} Slice ID: {}".format(dlg_object.delegation_id, dlg_object.slice.get_slice_id()))
        if dlg_object.delegation_name is not None:
            print("Delegation Name: {}".format(dlg_object.delegation_name))
        if dlg_object.site is not None:
            print("Site Name: {}".format(dlg_object.site))
        if dlg_object.sequence is not None:
            print("Sequence: {}".format(dlg_object.sequence))
        if dlg_object.state is not None:
            print(f"State: {DelegationState(dlg_object.state)}")
        if dlg_object.graph is not None:
            print("Graph: {}".format(dlg_object.graph))
        print("")

    @staticmethod
    def __print_delegations_json(*, delegations: List[DelegationAvro]):
        """
        Prints the Delegation Object
        """
        dlg_list = []
        for dlg_object in delegations:
            dlg_dict = {
                'name': dlg_object.get_name(),
                'dlg_id': dlg_object.get_delegation_id(),
                'slice_id': dlg_object.get_delegation_id(),
                'sequence': dlg_object.get_sequence(),
                'state': str(DelegationState(dlg_object.state)),
                'graph': dlg_object.graph
            }
            dlg_list.append(dlg_dict)
        print(json.dumps(dlg_list, indent=4))

    def __print_delegations(self, *, delegations: List[DelegationAvro], format: str):
        if format == 'text':
            for d in delegations:
                self.__print_delegation(dlg_object=d)
        else:
            self.__print_delegations_json(delegations=delegations)

    def do_get_sites(self, *, actor_name: str, callback_topic: str, sites: str) -> Tuple[List[SiteAvro] or None, Error]:
        actor = self.get_actor(actor_name=actor_name)

        if actor is None:
            raise Exception("Invalid arguments actor {} not found".format(actor_name))
        try:
            actor.prepare(callback_topic=callback_topic)
            return actor.get_sites(site=sites.upper()), actor.get_last_error()
        except Exception as e:
            self.logger.error(f"Exception occurred while fetching delegations: e {e}")
            self.logger.error(traceback.format_exc())
            traceback.print_exc()
        return None, actor.get_last_error()

    def get_sites(self, *, actor_name: str, callback_topic: str, sites: str, format: str):
        try:
            sites, error = self.do_get_sites(actor_name=actor_name, callback_topic=callback_topic, sites=sites)
            if sites is not None and len(sites) > 0:
                self.__print_sites(sites=sites, format=format, actor_name=actor_name)
            else:
                print(f"Status of {actor_name}: {error.get_status()}")
        except Exception as e:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
            print("Exception occurred while processing get_delegations {}".format(e))

    def __print_sites(self, *, sites: List[SiteAvro], format: str, actor_name: str):
        if format == 'text':
            print(f"Actor: {actor_name}")
            for s in sites:
                print(s)
        else:
            site_list = []
            for s in sites:
                s_dict = {
                    'name': s.get_name(),
                    'maint_info': s.get_maint_info().to_json()
                }
                site_list.append(s_dict)
            maint_info = {actor_name: site_list}
            print(json.dumps(maint_info, indent=4))

    @staticmethod
    def __extract_device_addr_octets(*, device_address: str) -> List[str]:
        """
        Function to extract PCI domain, bus, slot and function from BDF
        :param device_address BDF
        :return list containing PCI domain, bus, slot and function from BDF
        """
        match = re.split("(.*):(.*):(.*)\\.(.*)", device_address)
        result = []
        match = match[1:-1]
        for octet in match:
            octet = octet.lstrip("0")
            if octet == "":
                octet = '0x0'
            else:
                octet = f"0x{octet}"

            result.append(octet)
        return result