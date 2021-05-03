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

from fabric_cf.actor.core.manage.error import Error
from fabric_cf.actor.core.util.id import ID
from fabric_mb.message_bus.messages.delegation_avro import DelegationAvro
from fabric_mb.message_bus.messages.reservation_mng import ReservationMng
from fabric_mb.message_bus.messages.slice_avro import SliceAvro

from fabric_mgmt_cli.managecli.command import Command


class ShowCommand(Command):
    def get_slices(self, *, actor_name: str, callback_topic: str, slice_id: str, id_token: str):
        try:
            slices, error = self.do_get_slices(actor_name=actor_name, callback_topic=callback_topic, slice_id=slice_id,
                                               id_token=id_token)
            if slices is not None and len(slices) > 0:
                for s in slices:
                    s.print()
            else:
                print("Status: {}".format(error.get_status()))
        except Exception as e:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
            print("Exception occurred while processing get_slices {}".format(e))

    def get_reservations(self, *, actor_name: str, callback_topic: str, rid: str, id_token: str):
        try:
            reservations, error = self.do_get_reservations(actor_name=actor_name, callback_topic=callback_topic,
                                                           rid=rid, id_token=id_token)
            if reservations is not None and len(reservations) > 0:
                for r in reservations:
                    r.print()
            else:
                print("Status: {}".format(error.get_status()))
        except Exception as e:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
            print("Exception occurred while processing get_reservations {}".format(e))

    def get_delegations(self, *, actor_name: str, callback_topic: str, did: str, id_token: str):
        try:
            delegations, error = self.do_get_delegations(actor_name=actor_name, callback_topic=callback_topic,
                                                         did=did, id_token=id_token)
            if delegations is not None and len(delegations) > 0:
                for d in delegations:
                    d.print()
            else:
                print("Status: {}".format(error.get_status()))
        except Exception as e:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
            print("Exception occurred while processing get_delegations {}".format(e))

    def do_get_slices(self, *, actor_name: str, callback_topic: str, slice_id: str = None,
                      id_token: str = None) -> Tuple[List[SliceAvro], Error]:
        actor = self.get_actor(actor_name=actor_name)

        if actor is None:
            raise Exception("Invalid arguments actor {} not found".format(actor_name))
        try:
            actor.prepare(callback_topic=callback_topic)
            sid = None
            if slice_id is not None:
                sid = ID(uid=slice_id)
            return actor.get_slices(id_token=id_token, slice_id=sid), actor.get_last_error()
        except Exception:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
        return None, actor.get_last_error()

    def do_get_reservations(self, *, actor_name: str, callback_topic: str, rid: str = None,
                            id_token: str = None) -> Tuple[List[ReservationMng], Error]:
        actor = self.get_actor(actor_name=actor_name)

        if actor is None:
            raise Exception("Invalid arguments actor {} not found".format(actor_name))
        try:
            actor.prepare(callback_topic=callback_topic)
            reservation_id = None
            if rid is not None:
                reservation_id = ID(uid=rid)
            return actor.get_reservations(id_token=id_token, rid=reservation_id), actor.get_last_error()
        except Exception as e:
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
        return None, actor.get_last_error()

    def do_get_delegations(self, *, actor_name: str, callback_topic: str, did: str = None,
                           id_token: str = None) -> Tuple[List[DelegationAvro], Error]:
        actor = self.get_actor(actor_name=actor_name)

        if actor is None:
            raise Exception("Invalid arguments actor {} not found".format(actor_name))
        try:
            actor.prepare(callback_topic=callback_topic)
            return actor.get_delegations(id_token=id_token, delegation_id=did), actor.get_last_error()
        except Exception as e:
            traceback.print_exc()
            ex_str = traceback.format_exc()
            self.logger.error(ex_str)
        return None, actor.get_last_error()