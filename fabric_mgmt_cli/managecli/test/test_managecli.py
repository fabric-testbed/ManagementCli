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
import unittest

from click.testing import CliRunner
from fabric_mgmt_cli.managecli import managecli
import os


class ManageCliTest(unittest.TestCase):
    am_slice_id = 'b0176076-9fce-4084-88b0-490f22425af1'
    broker_slice_id = 'test_broker'
    am_res_id = 'test_res_am'
    broker_res_id = 'test_res_broker'
    os.environ['FABRIC_MGMT_CLI_CONFIG_PATH'] = "."

    def test_d_get_slices_am(self):
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['slices', 'query', '--actor', 'site1-am'])
        print("Result: {}".format(result.output))
        self.assertTrue(result.output.find("Slice Guid") != -1)

    def test_e_get_slices_broker(self):
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['slices', 'query', '--actor', 'broker'])
        print("Result: {}".format(result.output))
        self.assertTrue(result.output.find("Slice Guid") != -1)

    def test_f_get_slice_am(self):
        print("Using slice_id:{}".format(self.am_slice_id))
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['slices', 'query', '--actor', 'site1-am', '--sliceid',
                                                     ManageCliTest.am_slice_id])
        print("Result: {}".format(result.output))
        #self.assertTrue(result.output.find("ErrorNoSuchSlice") != -1)

    def test_g_get_slice_broker(self):
        print("Using slice_id:{}".format(self.broker_slice_id))
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['slices', 'query', '--actor', 'broker', '--sliceid',
                                                     ManageCliTest.broker_slice_id])
        print("Result: {}".format(result.output))
        self.assertTrue(result.output.find("ErrorNoSuchSlice") != -1)

    def test_h_get_reservations_broker(self):
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['slivers', 'query', '--actor', 'broker'])
        print("Result: {}".format(result.output))
        self.assertTrue(result.output.find("Reservation ID") != -1)

    def test_i_get_reservations_am(self):
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['slivers', 'query', '--actor', 'site1-am'])
        print("Result: {}".format(result.output))
        self.assertTrue(result.output.find("Reservation ID") != -1)

    def test_j_get_reservation(self):
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['slivers', 'query', '--actor', 'broker', '--rid',
                                                     ManageCliTest.broker_res_id])
        print("Result: {}".format(result.output))
        self.assertTrue(result.output.find("ErrorNoSuchReservation") != -1)

    def test_k_get_reservation(self):
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['slivers', 'query', '--actor', 'site1-am', '--rid',
                                                     ManageCliTest.am_res_id])
        print("Result: {}".format(result.output))
        self.assertTrue(result.output.find("ErrorNoSuchReservation") != -1)

    def test_l_close_reservation(self):
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['slivers', 'close', '--actor', 'broker', '--rid',
                                                     ManageCliTest.am_res_id])
        print("Result: {}".format(result.output))
        self.assertTrue(result.output.find('False') != -1)

    def test_m_close_slice(self):
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['slices', 'close', '--actor', 'broker', '--sliceid',
                                                     ManageCliTest.broker_slice_id])
        print("Result: {}".format(result.output))
        self.assertTrue(result.output.find('False') != -1)

    def test_n_remove_reservation(self):
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['slivers', 'remove', '--actor', 'broker', '--rid',
                                                     ManageCliTest.am_res_id])
        print("Result: {}".format(result.output))
        self.assertTrue(result.output.find('True') != -1)

    def test_o_remove_slice(self):
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['slices', 'remove', '--actor', 'broker', '--sliceid',
                                                     ManageCliTest.broker_slice_id])
        print("Result: {}".format(result.output))
        self.assertTrue(result.output.find('True') != -1)

    def test_p_claim_resources(self):
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['delegations', 'claim', '--broker', 'broker', '--am',
                                                     'site1-am'])
        print("Result: {}".format(result.output))
        #self.assertTrue(result.output.find("Code") == -1)

    def test_q_get_delegations_am(self):
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['delegations', 'show', '--actor', 'site1-am'])
        print(result.output)
        #self.assertTrue(result.exit_code != 0)

    def test_r_get_delegations_am_id_token(self):
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['delegations', 'show', '--actor', 'site1-am', '--idtoken', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJlbWFpbCI6Imt0aGFyZTEwQGVtYWlsLnVuYy5lZHUiLCJnaXZlbl9uYW1lIjoiS29tYWwiLCJmYW1pbHlfbmFtZSI6IlRoYXJlamEiLCJuYW1lIjoiS29tYWwgVGhhcmVqYSIsImlzcyI6Imh0dHBzOi8vY2lsb2dvbi5vcmciLCJzdWIiOiJodHRwOi8vY2lsb2dvbi5vcmcvc2VydmVyQS91c2Vycy8xMTkwNDEwMSIsImF1ZCI6ImNpbG9nb246L2NsaWVudF9pZC8xMjUzZGVmYzYwYTMyM2ZjYWEzYjQ0OTMyNjQ3NjA5OSIsInRva2VuX2lkIjoiaHR0cHM6Ly9jaWxvZ29uLm9yZy9vYXV0aDIvaWRUb2tlbi8zZjVkOWZmMTBlMzJiZTU3YjMzY2MwY2U5ZmI3OWE2Yy8xNjA0NTQ4NTY0MzE3IiwiYXV0aF90aW1lIjoiMTYwNDU0ODU2NCIsImV4cCI6MTYwNDU1MjE3MCwiaWF0IjoxNjA0NTQ4NTcwLCJyb2xlcyI6WyJDTzptZW1iZXJzOmFjdGl2ZSIsIkNPOkNPVTpKdXB5dGVyaHViOm1lbWJlcnM6YWN0aXZlIiwiQ086Q09VOnByb2plY3QtbGVhZHM6bWVtYmVyczphY3RpdmUiXSwic2NvcGUiOiJhbGwiLCJwcm9qZWN0IjoiYWxsIn0.CYIwHmz6k83OQaCZYYlQr-idK-7xdfFo3iLpw2nic7QkfREhmEMT5HPLUvKMuXDWteOtYqa62pMDsFynaZ6YQWW6r-1WzU57Xmff8uxrQwkNTe8Jgm6GVEEfRLaEXAjoRN1VfUWflMUOa2PLTPisIBtgbi9jqqUwJpZYiSgytIFr3amLwPKrdZVx0Hsx0ldycPzqeTgry7zLWQFF4WMFiRRw5dj43ma9Tzm34FXUE6_ZX5cmPuTpu7NWftrWIsSXdYtR81MIpG9F5a7bvSLyVxRKAqGxNEbELgkuANGSy9SlfMTZ3owBTzg_Rx1WJGhNRRTFlCP7MEbigjvrquNylg'])
        print(result.output)
        #self.assertTrue(result.exit_code != 0)


    def test_s_get_delegations_am_refresh_token(self):
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['delegations', 'delegations', '--actor', 'site1-am',
                                                     '--refreshtoken', 'https://cilogon.org/oauth2/refreshToken/592aeceab9fa39bff826ba3d829262c9/1604548564478'])
        print(result.output)
        #self.assertTrue(result.exit_code != 0)

    def test_q_get_delegations_broker(self):
        runner = CliRunner()
        result = runner.invoke(managecli.managecli, ['show', 'delegations', '--actor', 'broker'])
        print(result.output)
        #self.assertTrue(result.exit_code != 0)