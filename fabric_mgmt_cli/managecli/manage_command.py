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
import traceback
from datetime import datetime, timezone, timedelta
from typing import Tuple, Dict

from fabric_cf.actor.core.apis.abc_delegation import DelegationState
from fabric_cf.actor.core.common.constants import Constants
from fabric_cf.actor.core.kernel.reservation_states import ReservationStates
from fabric_cf.actor.core.kernel.slice_state_machine import SliceState
from fabric_cf.actor.core.manage.error import Error
from fabric_cf.actor.core.time.actor_clock import ActorClock
from fabric_cf.actor.core.util.id import ID
from fabric_mb.message_bus.messages.auth_avro import AuthAvro
from fabric_mb.message_bus.messages.delegation_avro import DelegationAvro
from fabric_mb.message_bus.messages.reservation_mng import ReservationMng
from fabric_mb.message_bus.messages.site_avro import SiteAvro
from fabric_mb.message_bus.messages.slice_avro import SliceAvro
from fim.slivers.maintenance_mode import MaintenanceInfo, MaintenanceEntry, MaintenanceState
from fim.slivers.network_node import NodeType
from fim.slivers.network_service import ServiceType

from fabric_mgmt_cli.managecli.show_command import ShowCommand


class ManageCommand(ShowCommand):
    def do_close_reservation(self, *, rid: str, actor_name: str, callback_topic: str,
                             id_token: str) -> Tuple[bool, Error]:
        """
        Close reservation by invoking Management Actor Close reservation API
        @param rid reservation id
        @param actor_name actor name
        @param callback_topic callback topic
        @param id_token identity token
        @return Tuple[bool, Error] indicating success or failure status and error containing failure details
        """
        actor = self.get_actor(actor_name=actor_name)
        if actor is None:
            raise Exception(f"Invalid arguments actor_name {actor_name} not found")

        try:
            actor.prepare(callback_topic=callback_topic)
            reservation_id = ID(uid=rid) if rid is not None else None
            return actor.close_reservation(rid=reservation_id), actor.get_last_error()
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

        return False, actor.get_last_error()

    def close_reservation(self, *, rid: str, actor_name: str, callback_topic: str, id_token: str):
        """
        Close reservation
        @param rid reservation id
        @param actor_name actor name
        @param callback_topic callback topic
        @param id_token identity token
        """
        try:
            result, error = self.do_close_reservation(rid=rid, actor_name=actor_name,
                                                      callback_topic=callback_topic, id_token=id_token)
            print(result)
            if result is False:
                self.print_result(status=error.get_status())
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

    def do_close_slice(self, *, slice_id: ID, actor_name: str, callback_topic: str,
                       id_token: str) -> Tuple[bool, Error]:
        """
        Close slice by invoking Management Actor Close reservations API
        @param slice_id slice id
        @param actor_name actor name
        @param callback_topic callback topic
        @param id_token identity token
        @return Tuple[bool, Error] indicating success or failure status and error containing failure details
        """
        actor = self.get_actor(actor_name=actor_name)
        if actor is None:
            raise Exception("Invalid arguments actor_name {} not found".format(actor_name))

        try:
            actor.prepare(callback_topic=callback_topic)
            return actor.close_reservations(slice_id=slice_id), actor.get_last_error()
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

        return False, actor.get_last_error()

    def close_slice(self, *, slice_id: str, actor_name: str, callback_topic: str, id_token: str):
        """
        Close slice
        @param slice_id slice id
        @param actor_name actor name
        @param callback_topic callback topic
        @param id_token identity token
        """
        try:
            sid = None
            if slice_id is not None:
                sid = ID(uid=slice_id)
            result, error = self.do_close_slice(slice_id=sid, actor_name=actor_name,
                                                callback_topic=callback_topic, id_token=id_token)
            print(result)
            if result is False:
                self.print_result(status=error.get_status())
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

    def do_remove_reservation(self, *, rid: str, actor_name: str, callback_topic: str,
                              id_token: str) -> Tuple[bool, Error]:
        """
        Remove reservation by invoking Management Actor Remove reservation API
        @param rid reservation id
        @param actor_name actor name
        @param callback_topic callback topic
        @param id_token identity token
        @return Tuple[bool, Error] indicating success or failure status and error containing failure details
        """
        actor = self.get_actor(actor_name=actor_name)
        if actor is None:
            raise Exception("Invalid arguments actor_name {} not found".format(actor_name))

        try:
            actor.prepare(callback_topic=callback_topic)
            reservation_id = ID(uid=rid) if rid is not None else None
            return actor.remove_reservation(rid=reservation_id), actor.get_last_error()
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())
        return False, actor.get_last_error()

    def remove_reservation(self, *, rid: str, actor_name: str, callback_topic: str, id_token: str):
        """
        Remove reservation
        @param rid reservation id
        @param actor_name actor name
        @param callback_topic callback topic
        @param id_token identity token
        """
        try:
            result, error = self.do_remove_reservation(rid=rid, actor_name=actor_name, callback_topic=callback_topic,
                                                       id_token=id_token)
            print(result)
            if result is False:
                self.print_result(status=error.get_status())
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

    def do_remove_slice(self, *, slice_id: str, actor_name: str, callback_topic: str,
                        id_token: str) -> Tuple[bool, Error]:
        """
        Remove slice by invoking Management Actor remove slice API
        @param slice_id slice id
        @param actor_name actor name
        @param callback_topic callback topic
        @param id_token identity token
        @return Tuple[bool, Error] indicating success or failure status and error containing failure details
        """
        actor = self.get_actor(actor_name=actor_name)
        if actor is None:
            raise Exception("Invalid arguments actor_name {} not found".format(actor_name))

        try:
            actor.prepare(callback_topic=callback_topic)
            sid = ID(uid=slice_id) if slice_id is not None else None
            return actor.remove_slice(slice_id=sid), actor.get_last_error()
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())
        return False, actor.get_last_error()

    def remove_slice(self, *, slice_id: str, actor_name: str, callback_topic: str, id_token: str):
        """
        Remove slice
        @param slice_id slice id
        @param actor_name actor name
        @param callback_topic callback topic
        @param id_token identity token
        """
        try:
            result, error = self.do_remove_slice(slice_id=slice_id, actor_name=actor_name,
                                                 callback_topic=callback_topic, id_token=id_token)
            print(result)
            if result is False:
                self.print_result(status=error.get_status())
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

    def do_claim_delegations(self, *, broker: str, am_guid: ID, callback_topic: str, id_token: str = None,
                             did: str = None) -> Tuple[DelegationAvro, Error]:
        """
        Claim delegations by invoking Management Actor Claim Delegations API
        @param broker broker guid
        @param am_guid am guid
        @param callback_topic callback topic
        @param id_token id token
        @param did delegation id
        @return Tuple[Delegation, Error] Delegation on success and Error in case of failure
        """
        actor = self.get_actor(actor_name=broker)

        if actor is None:
            raise Exception("Invalid arguments actor {} not found".format(broker))
        try:
            actor.prepare(callback_topic=callback_topic)

            dlg = actor.claim_delegations(broker=am_guid, did=did)
            return dlg, actor.get_last_error()
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

        return None, actor.get_last_error()

    def claim_delegations(self, *, broker: str, am: str, callback_topic: str, did: str = None, id_token: str = None):
        """
        Claim delegations
        @param broker broker name
        @param am am name
        @param callback_topic callback topic
        @param id_token id token
        @param did delegation id
        """
        try:
            am_actor = self.get_actor(actor_name=am)
            broker_actor = self.get_actor(actor_name=broker)

            if am_actor is None or broker_actor is None:
                raise Exception("Invalid arguments am_actor {} or broker_actor {} not found".format(am_actor,
                                                                                                    broker_actor))
            delegations = []
            if did is None:
                delegations, error = self.do_get_delegations(actor_name=am, callback_topic=callback_topic, did=did,
                                                             id_token=id_token)
                if delegations is None:
                    print("Error occurred while getting delegations for actor: {}".format(am))
                    self.print_result(status=error.get_status())
                    return

                if delegations is None or len(delegations) == 0:
                    print("No delegations to be claimed from {} by {}:".format(am, broker))
                    return
            else:
                dd = DelegationAvro()
                dd.slice = SliceAvro()
                dd.slice.slice_name = broker
                dd.delegation_id = did
                delegations = [dd]

            claimed = False
            for d in delegations:
                if d.get_state() == DelegationState.Failed.value or d.get_state() == DelegationState.Closed.value:
                    continue
                if d.get_slice_object().get_slice_name() == broker:
                    print("Claiming Delegation# {}".format(d.get_delegation_id()))
                    delegation, error = self.do_claim_delegations(broker=broker, am_guid=am_actor.get_guid(),
                                                                  did=d.get_delegation_id(), callback_topic=callback_topic,
                                                                  id_token=id_token)
                    claimed = True
                    if delegation is not None:
                        print("Delegation claimed: {} ".format(delegation.get_delegation_id()))
                    else:
                        self.print_result(status=error.get_status())
            if not claimed:
                print(f"No delegations found for Broker# {broker}")
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

    def do_reclaim_delegations(self, *, broker: str, am_guid: ID, callback_topic: str, id_token: str = None,
                               did: str = None) -> Tuple[DelegationAvro, Error]:
        """
        Reclaim delegations by invoking Management Actor Claim Delegations API
        @param broker broker guid
        @param am_guid am guid
        @param callback_topic callback topic
        @param id_token id token
        @param did delegation id
        @return Tuple[Delegation, Error] Delegation on success and Error in case of failure
        """
        actor = self.get_actor(actor_name=broker)

        if actor is None:
            raise Exception("Invalid arguments actor {} not found".format(broker))
        try:
            actor.prepare(callback_topic=callback_topic)

            dlg = actor.reclaim_delegations(broker=am_guid, did=did)
            return dlg, actor.get_last_error()
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

        return None, actor.get_last_error()

    def reclaim_delegations(self, *, broker: str, am: str, callback_topic: str, did: str = None, id_token: str = None):
        """
        Claim delegations
        @param broker broker name
        @param am am name
        @param callback_topic callback topic
        @param id_token id token
        @param did delegation id
        """
        try:
            am_actor = self.get_actor(actor_name=am)
            broker_actor = self.get_actor(actor_name=broker)

            if am_actor is None or broker_actor is None:
                raise Exception("Invalid arguments am_actor {} or broker_actor {} not found".format(am_actor,
                                                                                                    broker_actor))

            if did is None:
                delegations, error = self.do_get_delegations(actor_name=am, callback_topic=callback_topic, did=did,
                                                             id_token=id_token)
            else:
                dd = DelegationAvro()
                dd.slice = SliceAvro()
                dd.slice.slice_name = broker
                dd.delegation_id = did
                dd.state = DelegationState.Delegated.value
                delegations = [dd]

            if delegations is None:
                print("Error occurred while getting delegations for actor: {}".format(am))
                self.print_result(status=error.get_status())
                return

            if delegations is None or len(delegations) == 0:
                print("No delegations to be reclaimed from {} by {}:".format(am, broker))
                return

            claimed = False
            for d in delegations:
                if d.get_state() == DelegationState.Failed.value or d.get_state() == DelegationState.Closed.value:
                    continue
                if d.get_slice_object().get_slice_name() == broker:
                    print("Reclaiming Delegation# {}".format(d.get_delegation_id()))
                    delegation, error = self.do_reclaim_delegations(broker=broker, am_guid=am_actor.get_guid(),
                                                                    did=d.get_delegation_id(),
                                                                    callback_topic=callback_topic,
                                                                    id_token=id_token)
                    claimed = True
                    if delegation is not None:
                        print("Delegation reclaimed: {} ".format(delegation.get_delegation_id()))
                    else:
                        self.print_result(status=error.get_status())
            if not claimed:
                print(f"No delegations found for Broker# {broker}")
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

    def toggle_maintenance_mode(self, *, actor_name: str, callback_topic: str, state: str, projects: str = None,
                                users: str = None, site_name: str = None, workers: str = None, deadline: str = None,
                                expected_end: str = None, id_token: str = None):
        """
        Toggle Maintenance Mode
        @param actor_name actor name
        @param callback_topic callback topic
        @param state Maintenance State
        @param projects comma separated list of project_ids allowed in maintenance
        @param users comma separated list of email address of the users allowed in maintenance
        @param site_name site name
        @param workers comma separated list of specific workers on a site which are in maintenance
        @param deadline start time for the Maintenance
        @param expected_end Expected End time for the Maintenance
        @param id_token id token
        """
        status = False
        error = ""
        try:
            actor = self.get_actor(actor_name=actor_name)

            if actor is None:
                raise Exception(f"Invalid arguments! {actor_name} not found")

            mode = MaintenanceState.from_string(state)

            if mode == MaintenanceState.PreMaint and deadline is None:
                raise Exception("Required parameter: deadline is missing!")

            if deadline is not None:
                try:
                    maint_start_time = datetime.fromisoformat(deadline)
                except Exception as e:
                    raise Exception(f"Deadline is not in ISO 8601 format")
                now = datetime.now(timezone.utc)
                if maint_start_time < now:
                    raise Exception(f"Deadline cannot be before current time {now}")

            if expected_end is not None:
                try:
                    expected_end_time = datetime.fromisoformat(deadline)
                except Exception as e:
                    raise Exception(f"Expected end is not in ISO 8601 format")
                now = datetime.now(timezone.utc)
                if expected_end_time < now:
                    raise Exception(f"Expected end cannot be before current time {now}")

            try:
                actor.prepare(callback_topic=callback_topic)
                sites = None
                if site_name is None:
                    site_name = Constants.ALL

                worker_list = [site_name.upper()]
                if workers is not None:
                    worker_list = workers.split(",")

                maint_info = MaintenanceInfo()
                for w in worker_list:
                    entry = MaintenanceEntry(state=state, deadline=deadline, expected_end=expected_end)
                    maint_info.add(w, entry)
                site_avro = SiteAvro(name=site_name.upper(), maint_info=maint_info)
                sites = [site_avro]

                status = actor.toggle_maintenance_mode(actor_guid=str(actor.get_guid()), sites=sites, projects=projects,
                                                       users=users, callback_topic=callback_topic)

            except Exception as e:
                self.logger.error(f"Exception occurred e: {e}")
                self.logger.error(traceback.format_exc())

            error = actor.get_last_error()
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())
            error = str(e)

        if status:
            print(f"Maintenance mode successfully set to {state} on {actor_name}")
        else:
            print(f"Failure to set maintenance mode: [{state}]; Error: [{error}]")

    def create_slice(self, *, actor_name: str, callback_topic: str, slice_id: str, slice_name: str):
        try:
            slices, error = self.do_get_slices(actor_name=actor_name, callback_topic=callback_topic, id_token=None,
                                               email=None, slice_name=slice_name, slice_id=slice_id)

            if slices is not None and len(slices) > 0:
                raise Exception(f"Slice already exists!")
            else:
                actor = self.get_actor(actor_name=actor_name)
                actor.prepare(callback_topic=callback_topic)
                slice_obj = SliceAvro()
                slice_obj.set_slice_name(value=slice_name)
                slice_obj.set_slice_id(slice_id=slice_id)
                slice_obj.inventory = True
                slice_obj.broker_client_slice = False
                slice_obj.description = f"Inventory slice for {actor_name}"
                auth = AuthAvro()
                auth.name = actor_name
                auth.guid = f"{actor_name}-guid"
                slice_obj.set_owner(value=auth)
                actor.add_slice(slice_obj=slice_obj)
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

    def delete_dead_slices(self, *, actor_name: str, callback_topic: str, id_token: str, email: str, slice_id: str = None):
        try:
            states = [SliceState.Closing.name, SliceState.Dead.name]
            if slice_id is not None:
                states = None
            slices, error = self.do_get_slices(actor_name=actor_name, callback_topic=callback_topic, id_token=id_token,
                                               email=email, slice_name=None, slice_id=slice_id, states=states)

            if slices is not None:
                for s in slices:
                    state = SliceState(s.get_state())
                    if state not in [SliceState.Closing, SliceState.Dead]:
                        continue
                    print(f"Attempting to remove reservations for slice {s.get_slice_id()} in state {state}")
                    reservations, error = self.do_get_reservations(actor_name=actor_name, callback_topic=callback_topic,
                                                                   id_token=id_token, slice_id=s.get_slice_id())

                    if reservations is None:
                        print(f"No reservations to remove for slice {s.get_slice_id()}")
                    else:
                        for r in reservations:
                            print(f"Attempting to remove reservation: {r.get_reservation_id()}")
                            self.do_remove_reservation(rid=r.get_reservation_id(), actor_name=actor_name,
                                                       callback_topic=callback_topic, id_token=id_token)

                    print(f"Attempting to remove slice: {s.get_slice_id()}")
                    self.remove_slice(slice_id=s.get_slice_id(), actor_name=actor_name,
                                      callback_topic=callback_topic, id_token=id_token)
            else:
                print("No Dead/closing slices to remove")
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

    def do_close_delegation(self, *, did: str, actor_name: str, callback_topic: str,
                            id_token: str) -> Tuple[bool, Error]:
        """
        Close delegation by invoking Management Actor Close delegation API
        @param did delegation id
        @param actor_name actor name
        @param callback_topic callback topic
        @param id_token identity token
        @return Tuple[bool, Error] indicating success or failure status and error containing failure details
        """
        actor = self.get_actor(actor_name=actor_name)
        if actor is None:
            raise Exception(f"Invalid arguments actor_name {actor_name} not found")

        try:
            actor.prepare(callback_topic=callback_topic)
            return actor.close_delegation(did=did), actor.get_last_error()
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

        return False, actor.get_last_error()

    def close_delegation(self, *, did: str, actor_name: str, callback_topic: str, id_token: str):
        """
        Close delegation
        @param did delegation id
        @param actor_name actor name
        @param callback_topic callback topic
        @param id_token identity token
        """
        try:
            result, error = self.do_close_delegation(did=did, actor_name=actor_name,
                                                     callback_topic=callback_topic, id_token=id_token)
            print(result)
            if result is False:
                self.print_result(status=error.get_status())
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

    def do_remove_delegation(self, *, did: str, actor_name: str, callback_topic: str,
                             id_token: str) -> Tuple[bool, Error]:
        """
        Remove delegation by invoking Management Actor Remove delegation API
        @param did delegation id
        @param actor_name actor name
        @param callback_topic callback topic
        @param id_token identity token
        @return Tuple[bool, Error] indicating success or failure status and error containing failure details
        """
        actor = self.get_actor(actor_name=actor_name)
        if actor is None:
            raise Exception("Invalid arguments actor_name {} not found".format(actor_name))

        try:
            actor.prepare(callback_topic=callback_topic)
            return actor.remove_delegation(did=did), actor.get_last_error()
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())
        return False, actor.get_last_error()

    def remove_delegation(self, *, did: str, actor_name: str, callback_topic: str, id_token: str):
        """
        Remove delegation
        @param did delegation id
        @param actor_name actor name
        @param callback_topic callback topic
        @param id_token identity token
        """
        try:
            result, error = self.do_remove_delegation(did=did, actor_name=actor_name,
                                                      callback_topic=callback_topic, id_token=id_token)
            print(result)
            if result is False:
                self.print_result(status=error.get_status())
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

    def __identify_inconsitent_sliver(self, first: Dict[str, ReservationMng], second: Dict[str, ReservationMng],
                                      third: Dict[str, ReservationMng], first_allowed_states: list,
                                      second_allowed_states: list, third_allowed_states: list,
                                      first_name: str, second_name: str, third_name: str):
        flag = False
        for sid, sliver in first.items():
            second_state = ReservationStates.Closed.value
            third_state = ReservationStates.Closed.value
            if sid in second:
                second_state = second[sid].get_state()
            if sid in third:
                third_state = third[sid].get_state()

            if sliver.get_state() in first_allowed_states and second_state in second_allowed_states and \
                    third_state in third_allowed_states:
                continue
            else:
                print(f"Sliver: {sliver.get_reservation_id()} Slice: {sliver.get_slice_id()} of "
                      f"type: {sliver.get_resource_type()} is inconsistent "
                      f"States: {ReservationStates(sliver.get_state())}/{first_name} "
                      f"{ReservationStates(second_state)}/{second_name} {ReservationStates(third_state)}/{third_name}")
                      #f" with Start: {self.time_string(milliseconds=sliver.get_start())} "
                      #f"End: {self.time_string(milliseconds=sliver.get_end())} "
                      #f"Requested End: {self.time_string(milliseconds=sliver.get_requested_end())}")
                flag = True
        if not flag:
            print(f"No inconsistencies found between {first} {second} {third}!")

    def do_audit(self, *, oc_name: str, br_name: str, am_name: str, site_name: str, slice_id: str,
                 sliver_id: str, callback_topic: str, sliver_type: str):
        if oc_name is None and br_name is None and am_name is None:
            raise Exception(f"Invalid arguments; must specify at least two actors")

        if site_name is None and "net" not in am_name and "al2s" not in am_name:
            site_name = am_name.split("-")[0].upper()

        if sliver_type is None:
            if "net" in am_name:
                sliver_type = ""
                for x in ServiceType:
                    sliver_type += f"{x},"
                if sliver_type != "":
                    sliver_type.removesuffix(",")
            else:
                sliver_type = f"{NodeType.VM}"

        oc_slivers = []
        br_slivers = []
        am_slivers = []
        states = "ticketed, activeticketed, active, failed"

        if oc_name is not None:
            oc_slivers, error = self.do_get_reservations(actor_name=oc_name, site=site_name,
                                                         slice_id=slice_id, rid=sliver_id,
                                                         callback_topic=callback_topic,
                                                         type=sliver_type, states=states)
            if oc_slivers is None:
                oc_slivers = []
                if error.get_status().get_code() != 0:
                    print("Status: {}".format(error.get_status()))

        if br_name is not None:
            br_slivers, error = self.do_get_reservations(actor_name=br_name, site=site_name,
                                                         slice_id=slice_id, rid=sliver_id,
                                                         callback_topic=callback_topic,
                                                         type=sliver_type, states=states)
            if br_slivers is None:
                br_slivers = []
                if error.get_status().get_code() != 0:
                    print("Status: {}".format(error.get_status()))

        if am_name is not None:
            am_slivers, error = self.do_get_reservations(actor_name=am_name, site=site_name,
                                                         slice_id=slice_id, rid=sliver_id,
                                                         callback_topic=callback_topic,
                                                         type=sliver_type, states=states)
            if am_slivers is None:
                am_slivers = []
                if error.get_status().get_code() != 0:
                    print("Status: {}".format(error.get_status()))

        no_oc_slivers = len(oc_slivers)
        no_br_slivers = len(br_slivers)
        no_am_slivers = len(am_slivers)

        oc_slivers_dict = {s.get_reservation_id(): s for s in oc_slivers}
        br_slivers_dict = {s.get_reservation_id(): s for s in br_slivers}
        am_slivers_dict = {s.get_reservation_id(): s for s in am_slivers}

        if no_oc_slivers > 0 and no_oc_slivers >= no_br_slivers and no_oc_slivers >= no_am_slivers:
            self.__identify_inconsitent_sliver(first=oc_slivers_dict, second=br_slivers_dict, third=am_slivers_dict,
                                               first_allowed_states=[ReservationStates.Active.value,
                                                                     ReservationStates.ActiveTicketed.value],
                                               second_allowed_states=[ReservationStates.Ticketed.value],
                                               third_allowed_states=[ReservationStates.Active.value,
                                                                     ReservationStates.ActiveTicketed.value],
                                               first_name=oc_name, second_name=br_name, third_name=am_name)

        elif no_br_slivers > 0 and no_br_slivers >= no_oc_slivers and no_br_slivers >= no_am_slivers:
            self.__identify_inconsitent_sliver(first=br_slivers_dict, second=oc_slivers_dict, third=am_slivers_dict,
                                               first_allowed_states=[ReservationStates.Ticketed.value],
                                               second_allowed_states=[ReservationStates.Active.value,
                                                                      ReservationStates.ActiveTicketed.value],
                                               third_allowed_states=[ReservationStates.Active.value,
                                                                     ReservationStates.ActiveTicketed.value],
                                               first_name=br_name, second_name=oc_name, third_name=am_name)

        elif no_am_slivers > 0 and no_am_slivers >= no_oc_slivers and no_am_slivers >= no_br_slivers:
            self.__identify_inconsitent_sliver(first=am_slivers_dict, second=br_slivers_dict, third=oc_slivers_dict,
                                               first_allowed_states=[ReservationStates.Active.value,
                                                                     ReservationStates.ActiveTicketed.value],
                                               second_allowed_states=[ReservationStates.Ticketed.value],
                                               third_allowed_states=[ReservationStates.Active.value,
                                                                     ReservationStates.ActiveTicketed.value],
                                               first_name=am_name, second_name=br_name, third_name=oc_name)
        else:
            print(f"No inconsistencies found between {oc_name} {br_name} {am_name}!")

    @staticmethod
    def extract_guid(*, string):
        import re
        uuid_regex = r"[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}"
        match = re.search(uuid_regex, string)
        if match:
            return str(match.group(0))
        else:
            return string

    def do_get_net_services(self):
        from fabric_mgmt_cli.managecli.net.commands import NetCommand
        net_cmd = NetCommand()
        net_cmd.get_services(None, None)
        if net_cmd._res is not None:
            new = dict()
            for k, v in net_cmd._res.items():
                if isinstance(v, dict):
                    for l, w in v.items():
                        if not isinstance(w, list):
                            continue
                        for d in w:
                            if isinstance(d, dict) and "name" in d:
                                guid = self.extract_guid(string=str(d['name']))
                                new[guid] = d
                                d['opts'] = l
                elif isinstance(v, list):
                    for d in v:
                        if isinstance(d, dict) and "name" in d:
                            guid = self.extract_guid(string=str(d['name']))
                            new[guid] = d
            return new
        else:
            self.logger.error(f"Error occurred while getting services: {net_cmd._code}")
        return None

    def do_audit_infra(self, *, am_name: str, site_name: str, slice_id: str, sliver_id: str, callback_topic: str,
                       sliver_type: str):
        if am_name is None:
            raise Exception(f"Invalid arguments; must specify at least two actors")

        if site_name is None and "net" not in am_name and "al2s" not in am_name:
            site_name = am_name.split("-")[0].upper()

        if sliver_type is None:
            if "net" in am_name:
                sliver_type = ""
                for x in ServiceType:
                    sliver_type += f"{x},"
                if sliver_type != "":
                    sliver_type.removesuffix(",")
            else:
                sliver_type = f"{NodeType.VM}"

        am_slivers = []
        if_slivers = {}
        states = "ticketed, activeticketed, active, failed"

        if am_name is not None:
            am_slivers, error = self.do_get_reservations(actor_name=am_name, site=site_name,
                                                         slice_id=slice_id, rid=sliver_id,
                                                         callback_topic=callback_topic,
                                                         type=sliver_type, states=states)
            if am_slivers is None:
                am_slivers = []
                if error.get_status().get_code() != 0:
                    print("Status: {}".format(error.get_status()))

        if "net" in am_name:
            if_slivers = self.do_get_net_services()
            if if_slivers is None:
                if_slivers = {}

        am_slivers_dict = {s.get_reservation_id(): s for s in am_slivers}

        if len(am_slivers_dict) >= len(if_slivers):
            for sid, sliver in am_slivers_dict.items():
                sliver_state = ReservationStates(sliver.get_state())
                msg = f"--service {str(sliver.get_resource_type()).lower()}  --name " \
                      f"{sliver.get_name()}-{sliver.get_reservation_id()} of Slice: {sliver.get_slice_id()} "\
                      f" is inconsistent (cf_state/if_state): ({sliver_state}/"
                if sliver_state == ReservationStates.Active and sid in if_slivers:
                    continue
                else:
                    if sid in if_slivers:
                            msg += f"Provisioned)"
                    else:
                        msg += f"Not Provisioned)"
                    print(msg)
        elif len(am_slivers_dict) < len(if_slivers):
            for name, if_sliver in if_slivers.items():
                if if_sliver.get('opts'):
                    if_sliver_type = if_sliver['opts'].split(":")[0].upper()
                else:
                    if_sliver_type = ""
                msg = f"--service {if_sliver_type.lower()} --name {if_sliver['name']} " \
                      f"is inconsistent (if_state/cf_state): (Provisioned/"
                if name in am_slivers_dict and am_slivers_dict[name].get_state() == ReservationStates.Active.value:
                    continue
                else:
                    if name in am_slivers_dict:
                        msg += f"{ReservationStates(am_slivers_dict[name].get_state())})"
                    else:
                        msg += f"Closed)"
                    print(msg)
        else:
            print(f"No inconsistencies found between {am_name} and infrastructure!")

    def __validate_lease_end_time(self, lease_end_time: str) -> datetime:
        """
        Validate Lease End Time
        :param lease_end_time: New End Time
        :return End Time
        :raises Exception if new end time is in past
        """
        new_end_time = None
        if lease_end_time is None:
            new_end_time = datetime.now(timezone.utc) + timedelta(hours=Constants.DEFAULT_LEASE_IN_HOURS)
            return new_end_time
        try:
            new_end_time = datetime.strptime(lease_end_time, Constants.LEASE_TIME_FORMAT)
        except Exception as e:
            raise Exception(f"Lease End Time is not in format {Constants.LEASE_TIME_FORMAT}")

        now = datetime.now(timezone.utc)
        if new_end_time <= now:
            raise Exception(f"New term end time {new_end_time} is in the past! ")

        if (new_end_time - now) > Constants.DEFAULT_MAX_DURATION:
            self.logger.info(f"New term end time {new_end_time} exceeds system default "
                             f"{Constants.DEFAULT_MAX_DURATION}, setting to system default: ")

            new_end_time = now + Constants.DEFAULT_MAX_DURATION

        return new_end_time

    def do_renew_slice(self, *, slice_id: str, actor_name: str, callback_topic: str, end_time: str) -> bool:
        """
        Renew slice by invoking Management Actor Renew reservations API
        @param slice_id slice id
        @param actor_name actor name
        @param callback_topic callback topic
        @param end_time end time
        @return Tuple[bool, Error] indicating success or failure status and error containing failure details
        """
        actor = self.get_actor(actor_name=actor_name)
        if actor is None:
            raise Exception("Invalid arguments actor_name {} not found".format(actor_name))

        new_end_time = self.__validate_lease_end_time(lease_end_time=end_time)

        slices, error = self.do_get_slices(actor_name=actor_name, slice_id=slice_id, callback_topic=callback_topic)

        if slices is None:
            raise Exception(f"Slice {slice_id} Not Found")

        slice_object = slices[0]

        slivers, error = self.do_get_reservations(actor_name=actor_name, slice_id=slice_id,
                                                  callback_topic=callback_topic)

        if slivers is None:
            raise Exception(f"Slivers for slice {slice_id} Not Found")

        failed_to_extend_rid_list = []

        actor.prepare(callback_topic=callback_topic)
        for r in slivers:
            res_state = ReservationStates(r.get_state())
            if res_state == ReservationStates.Closed or res_state == ReservationStates.Failed or \
                    res_state == ReservationStates.CloseWait:
                continue

            current_end_time = ActorClock.from_milliseconds(milli_seconds=r.get_end())

            if new_end_time < current_end_time:
                raise Exception(f"Attempted new term end time is shorter than current slice end time")

            self.logger.debug(f"Extending reservation with reservation# {r.get_reservation_id()}")
            result = actor.extend_reservation(reservation=ID(uid=r.get_reservation_id()),
                                              new_end_time=new_end_time,
                                              sliver=None)
            if not result:
                self.logger.error(f"Error: {actor.get_last_error()}")
                failed_to_extend_rid_list.append(r.get_reservation_id())

        if len(failed_to_extend_rid_list) == 0:
            slice_object.set_lease_end(lease_end=new_end_time)
            if not actor.update_slice(slice_obj=slice_object):
                self.logger.error(f"Failed to update lease end time: {new_end_time} in Slice: {slice_object}")
                self.logger.error(actor.get_last_error())

        if len(failed_to_extend_rid_list) > 0:
            raise Exception(f"Failed to extend reservation# {failed_to_extend_rid_list}")

        return True

    def renew_slice(self, *, slice_id: str, actor_name: str, callback_topic: str, end_time: str):
        """
        Close slice
        @param slice_id slice id
        @param actor_name actor name
        @param callback_topic callback topic
        @param end_time end time
        """
        try:
            self.do_renew_slice(slice_id=slice_id, actor_name=actor_name, callback_topic=callback_topic,
                                end_time=end_time)
            print(f"Slice {slice_id} renewed successfully!")
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())
            print(f"Failed to renew slice: {slice_id} error: {e}")