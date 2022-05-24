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
from typing import Tuple, List

from fabric_cf.actor.core.apis.abc_delegation import DelegationState
from fabric_cf.actor.core.common.constants import Constants
from fabric_cf.actor.core.kernel.reservation_states import ReservationStates, ReservationPendingStates
from fabric_cf.actor.core.kernel.slice_state_machine import SliceState
from fabric_cf.actor.core.manage.error import Error
from fabric_cf.actor.core.time.actor_clock import ActorClock
from fabric_cf.actor.core.util.id import ID
from fabric_mb.message_bus.messages.delegation_avro import DelegationAvro
from fabric_mb.message_bus.messages.reservation_mng import ReservationMng
from fabric_mb.message_bus.messages.slice_avro import SliceAvro
from fim.slivers.network_node import NodeSliver
from fim.slivers.network_service import NetworkServiceSliver

from fabric_mgmt_cli.managecli.command import Command


class ShowCommand(Command):
    def get_slices(self, *, actor_name: str, callback_topic: str, slice_id: str, slice_name: str, id_token: str,
                   email: str):
        try:
            slices, error = self.do_get_slices(actor_name=actor_name, callback_topic=callback_topic, slice_id=slice_id,
                                               slice_name=slice_name, id_token=id_token, email=email)
            if slices is not None and len(slices) > 0:
                for s in slices:
                    self.__print_slice(slice_object=s)
            else:
                print("Status: {}".format(error.get_status()))
        except Exception as e:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
            print("Exception occurred while processing get_slices {}".format(e))

    def get_reservations(self, *, actor_name: str, callback_topic: str, slice_id: str, rid: str,
                         state: str, id_token: str, email: str):
        try:
            reservations, error = self.do_get_reservations(actor_name=actor_name, callback_topic=callback_topic,
                                                           slice_id=slice_id, rid=rid, state=state, id_token=id_token,
                                                           email=email)
            if reservations is not None and len(reservations) > 0:
                for r in reservations:
                    self.__print_reservation(reservation=r, detailed=(rid is not None))
            else:
                print("Status: {}".format(error.get_status()))
        except Exception as e:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
            print("Exception occurred while processing get_reservations {}".format(e))

    def get_delegations(self, *, actor_name: str, callback_topic: str, slice_id: str, did: str, state: str,
                        id_token: str):
        try:
            delegations, error = self.do_get_delegations(actor_name=actor_name, callback_topic=callback_topic,
                                                         slice_id=slice_id, did=did, state=state, id_token=id_token)
            if delegations is not None and len(delegations) > 0:
                for d in delegations:
                    d.print()
            else:
                print("Status: {}".format(error.get_status()))
        except Exception as e:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
            print("Exception occurred while processing get_delegations {}".format(e))

    def do_get_slices(self, *, actor_name: str, callback_topic: str, slice_id: str = None, slice_name: str,
                      id_token: str = None, email: str = None) -> Tuple[List[SliceAvro], Error]:
        actor = self.get_actor(actor_name=actor_name)

        if actor is None:
            raise Exception("Invalid arguments actor {} not found".format(actor_name))
        try:
            actor.prepare(callback_topic=callback_topic)
            sid = ID(uid=slice_id) if slice_id is not None else None
            return actor.get_slices(slice_id=sid, slice_name=slice_name, email=email), actor.get_last_error()
        except Exception:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
        return None, actor.get_last_error()

    def do_get_reservations(self, *, actor_name: str, callback_topic: str, slice_id: str = None, rid: str = None,
                            state: str = None, id_token: str = None,
                            email: str = None) -> Tuple[List[ReservationMng], Error]:
        actor = self.get_actor(actor_name=actor_name)

        if actor is None:
            raise Exception("Invalid arguments actor {} not found".format(actor_name))
        try:
            actor.prepare(callback_topic=callback_topic)
            sid = ID(uid=slice_id) if slice_id is not None else None
            reservation_id = ID(uid=rid) if rid is not None else None
            reservation_state = None
            if state is not None and state != "all":
                reservation_state = ReservationStates.translate(state_name=state).value
            return actor.get_reservations(slice_id=sid, rid=reservation_id,
                                          state=reservation_state, email=email), actor.get_last_error()
        except Exception as e:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
        return None, actor.get_last_error()

    def do_get_delegations(self, *, actor_name: str, callback_topic: str, slice_id: str = None, did: str = None,
                           state: str = None, id_token: str = None) -> Tuple[List[DelegationAvro], Error]:
        actor = self.get_actor(actor_name=actor_name)

        if actor is None:
            raise Exception("Invalid arguments actor {} not found".format(actor_name))
        try:
            actor.prepare(callback_topic=callback_topic)
            sid = None
            if slice_id is not None:
                sid = ID(uid=slice_id)
            delegation_state = None
            if state is not None and state != "all":
                delegation_state = DelegationState.translate(state_name=state).value
            return actor.get_delegations(delegation_id=did, slice_id=sid,
                                         state=delegation_state), actor.get_last_error()
        except Exception as e:
            traceback.print_exc()
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
        return None, actor.get_last_error()

    @staticmethod
    def __print_reservation(*, reservation: ReservationMng, detailed: bool = False):
        """
        Prints ReservationMng
        """
        print("")
        print(f"Reservation ID: {reservation.reservation_id} Slice ID: {reservation.slice_id}")
        if reservation.rtype is not None or reservation.notices is not None:
            print(f"Resource Type: {reservation.rtype} Notices: {reservation.notices}")

        if reservation.start is not None or reservation.end is not None or reservation.requested_end is not None:
            print(f"Start: {ShowCommand.__time_string(milliseconds=reservation.start)} "
                  f"End: {ShowCommand.__time_string(milliseconds=reservation.end)} "
                  f"Requested End: {ShowCommand.__time_string(milliseconds=reservation.requested_end)}")

        if reservation.units is not None or reservation.state is not None or reservation.pending_state is not None:
            print(f"Units: {reservation.units} State: {ReservationStates(reservation.state)} "
                  f"Pending State: {ReservationPendingStates(reservation.pending_state)}")

        sliver = reservation.get_sliver()
        if sliver is not None:
            print(f"Sliver: {sliver}")
            if detailed:
                if isinstance(sliver, NodeSliver):
                    ShowCommand.__print_node_sliver(sliver=sliver)
                elif isinstance(sliver, NetworkServiceSliver):
                    ShowCommand.__print_ns_sliver(sliver=sliver)
        print("")

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
    def __time_string(*, milliseconds):
        time_obj = ActorClock.from_milliseconds(milli_seconds=milliseconds)
        return time_obj.strftime(Constants.LEASE_TIME_FORMAT)

    @staticmethod
    def __print_slice(*, slice_object: SliceAvro):
        """
        Prints Slice Object
        """
        print("")
        print(f"Slice Name: {slice_object.get_slice_name()} Slice ID: {slice_object.get_slice_id()} "
              f"Project ID: {slice_object.get_slice_id()}")
        if slice_object.get_graph_id() is not None:
            print(f"Graph ID: {slice_object.get_graph_id()}")

        if slice_object.get_owner() is not None:
            print(f"Slice owner: {slice_object.get_owner()}")

        if slice_object.get_state() is not None:
            print(f"Slice state: {SliceState(slice_object.get_state())}")

        if slice_object.get_lease_end() is not None:
            print(f"Lease time: {slice_object.get_lease_end()}")
        print("")
