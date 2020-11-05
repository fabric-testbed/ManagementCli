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
import os
from fabric.credmgr import swagger_client
from fabric.credmgr.swagger_client.rest import ApiException as CredMgrException


class TokenException(Exception):
    pass


class CredentialManager(object):
    @staticmethod
    def get_token(*, project_name: str = 'all', scope: str = 'all', refresh_token: str, host: str):
        if host is None:
            raise Exception("Missing Credential Manager Host")

        if refresh_token is None or refresh_token == "":
            raise Exception("Please visit Credential Manager at {}/ui/ and use POST /tokens/create command to " \
                            "generate fabric tokens!\nSet up the environment variables for FABRIC_ID_TOKEN and " \
                            "FABRIC_REFRESH_TOKEN".format(host))

        result = CredentialManager.refresh_token(project_name=project_name, scope=scope, refresh_token=refresh_token,
                                               host=host)
        os.environ['FABRIC_REFRESH_TOKEN'] = result.get('refresh_token')
        return result

    @staticmethod
    def refresh_token(*, project_name: str = 'all', scope: str = 'all', refresh_token: str, host: str):
        try:
            # revoke tokens for an user
            configuration = swagger_client.configuration.Configuration()
            configuration.host = host
            api_instance = swagger_client.ApiClient(configuration)

            body = swagger_client.Request(refresh_token)
            tokens_api = swagger_client.TokensApi(api_client=api_instance)
            api_response = tokens_api.tokens_refresh_post(body=body,
                                                          project_name=project_name,
                                                          scope=scope)
            return api_response.to_dict()
        except CredMgrException as e:
            #traceback.print_exc()
            raise Exception(e.reason, e.body)
