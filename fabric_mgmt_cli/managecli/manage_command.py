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
from typing import Tuple

from fabric_cf.actor.core.apis.abc_delegation import DelegationState
from fabric_cf.actor.core.kernel.slice_state_machine import SliceState
from fabric_cf.actor.core.manage.error import Error
from fabric_cf.actor.core.util.id import ID
from fabric_mb.message_bus.messages.delegation_avro import DelegationAvro
from fabric_mb.message_bus.messages.slice_avro import SliceAvro

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

            delegations, error = self.do_get_delegations(actor_name=am, callback_topic=callback_topic, did=did,
                                                         id_token=id_token)
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

    def toggle_maintenance_mode(self, *, actor_name: str, callback_topic: str, mode: bool = False,
                                id_token: str = None):
        """
        Claim delegations
        @param actor_name actor name
        @param callback_topic callback topic
        @param mode mode
        @param id_token id token
        """
        status = False
        error = ""
        try:
            actor = self.get_actor(actor_name=actor_name)

            if actor is None:
                raise Exception(f"Invalid arguments! {actor_name} not found")

            try:
                actor.prepare(callback_topic=callback_topic)

                status = actor.toggle_maintenance_mode(actor_guid=str(actor.get_guid()),
                                                       mode=mode, callback_topic=callback_topic)
            except Exception as e:
                self.logger.error(f"Exception occurred e: {e}")
                self.logger.error(traceback.format_exc())

            error = actor.get_last_error()
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())
            error = str(e)

        if status:
            print(f"Maintenance mode successfully set to {mode}")
        else:
            print(f"Failure to set maintenance mode error {error}")

    def delete_dead_slices(self, *, actor_name: str, callback_topic: str, id_token: str, email: str):

        try:
            slices, error = self.do_get_slices(actor_name=actor_name, callback_topic=callback_topic, id_token=id_token,
                                               email=email, slice_name=None)

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