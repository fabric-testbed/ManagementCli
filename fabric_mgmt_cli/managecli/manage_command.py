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

from fabric_cf.actor.core.manage.error import Error
from fabric_cf.actor.core.util.id import ID
from fabric_mb.message_bus.messages.delegation_avro import DelegationAvro

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
            return actor.close_reservation(rid=ID(uid=rid)), actor.get_last_error()
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
            result, error = self.do_close_slice(slice_id=ID(uid=slice_id), actor_name=actor_name,
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
            return actor.remove_reservation(rid=ID(uid=rid)), actor.get_last_error()
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
            return actor.remove_slice(slice_id=ID(uid=slice_id)), actor.get_last_error()
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

    def do_claim_resources(self, *, broker: str, am_guid: ID, callback_topic: str, id_token: str,
                           did: str) -> Tuple[DelegationAvro, Error]:
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

            dlg = actor.claim_delegations(broker=am_guid, did=did, id_token=id_token)
            return dlg, actor.get_last_error()
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

        return None, actor.get_last_error()

    def claim_delegations(self, *, broker: str, am: str, callback_topic: str, did: str, id_token: str):
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

            broker_slice_id_list = []
            if did is None:
                slices, error = self.do_get_slices(actor_name=am, callback_topic=callback_topic, slice_id=None,
                                                   id_token=id_token)
                if slices is None:
                    print("Error occurred while getting slices for actor: {}".format(am))
                    self.print_result(status=error.get_status())
                    return

                for s in slices:
                    if s.get_slice_name() == broker:
                        broker_slice_id_list.append(s.get_slice_id())

            delegations, error = self.do_get_delegations(actor_name=am, callback_topic=callback_topic, did=did,
                                                         id_token=id_token)
            if delegations is None:
                print("Error occurred while getting delegations for actor: {}".format(am))
                self.print_result(status=error.get_status())
                return

            if delegations is None or len(delegations) == 0:
                print("No delegations to be claimed from {} by {}:".format(am, broker))
                return

            for d in delegations:
                print("Claiming Delegation# {}".format(d.get_delegation_id()))
                delegation, error = self.do_claim_resources(broker=broker, am_guid=am_actor.get_guid(),
                                                             did=d.get_delegation_id(), callback_topic=callback_topic,
                                                            id_token=id_token)
                if delegation is not None:
                    print("Delegation claimed: {} ".format(delegation.get_delegation_id()))
                else:
                    self.print_result(status=error.get_status())
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

    def do_reclaim_resources(self, *, broker: str, am_guid: ID, callback_topic: str, id_token: str,
                             did: str = None) -> Tuple[DelegationAvro, Error]:
        """
        ReClaim delegations by invoking Management Actor ReClaim Delegations API
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
            return actor.reclaim_delegations(broker=am_guid, did=did, id_token=id_token), \
                   actor.get_last_error()
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())

        return None, actor.get_last_error()

    def reclaim_delegations(self, *, broker: str, am: str, callback_topic: str, did: str, id_token: str):
        """
        ReClaim delegations
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

            reclaim_rid_list = {}
            broker_slice_id_list = []
            if did is None:
                slices, error = self.do_get_slices(actor_name=am, callback_topic=callback_topic, slice_id=None,
                                                   id_token=id_token)
                if slices is None:
                    print("Error occurred while getting slices for actor: {}".format(am))
                    self.print_result(status=error.get_status())
                    return

                for s in slices:
                    if s.get_slice_name() == broker:
                        broker_slice_id_list.append(s.get_slice_id())

            delegations, error = self.do_get_delegations(actor_name=am, callback_topic=callback_topic, did=did,
                                                         id_token=id_token)
            if delegations is None or len(reclaim_rid_list) == 0:
                print("No delegations to be claimed from {} by {}:".format(am, broker))
                return

            for d in delegations:
                print("Reclaiming Delegation# {}".format(d.get_delegation_id()))
                delegation, error = self.do_reclaim_resources(broker=broker, am_guid=am_actor.get_guid(),
                                                              did=d.get_delegation_id(), callback_topic=callback_topic,
                                                              id_token=id_token)
                if delegation is not None:
                    print("Delegation reclaimed: {} ".format(delegation.get_delegation_id()))
                else:
                    self.print_result(status=error.get_status())
        except Exception as e:
            self.logger.error(f"Exception occurred e: {e}")
            self.logger.error(traceback.format_exc())