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
import click

from fabric_mgmt_cli.managecli.kafka_processor import KafkaProcessorSingleton
from fabric_mgmt_cli.managecli.manage_command import ManageCommand
from fabric_mgmt_cli.managecli.show_command import ShowCommand
from fabric_mgmt_cli.managecli.net import commands as netcommands


@click.group()
@click.option('-v', '--verbose', is_flag=True)
@click.pass_context
def managecli(ctx, verbose):
    ctx.ensure_object(dict)
    ctx.obj['VERBOSE'] = verbose


@click.group()
@click.pass_context
def slices(ctx):
    """ Slice management
    """
    config = os.getenv('FABRIC_MGMT_CLI_CONFIG_PATH')
    if config is None or config == "":
        ctx.fail('FABRIC_MGMT_CLI_CONFIG_PATH is not set')

    return


@slices.command()
@click.option('--sliceid', help='Slice Id', required=True)
@click.option('--actor', help='Actor Name', required=True)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def close(ctx, sliceid, actor, idtoken, refreshtoken):
    """ Closes slice for an actor
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ManageCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.close_slice(slice_id=sliceid, actor_name=actor,
                                 callback_topic=KafkaProcessorSingleton.get().get_callback_topic(), id_token=idtoken)
        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


@slices.command()
@click.option('--sliceid', help='Slice Id', required=True)
@click.option('--actor', help='Actor Name', required=True)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def remove(ctx, sliceid, actor, idtoken, refreshtoken):
    """ Removes slice for an actor
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ManageCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.remove_slice(slice_id=sliceid, actor_name=actor,
                                  callback_topic=KafkaProcessorSingleton.get().get_callback_topic(), id_token=idtoken)
        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


@slices.command()
@click.option('--email', help='User Email', required=True)
@click.option('--actor', help='Actor Name', required=True)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def removealldead(ctx, email, actor, idtoken, refreshtoken):
    """ Removes slice for an actor
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ManageCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.delete_dead_slices(email=email, actor_name=actor, id_token=idtoken,
                                        callback_topic=KafkaProcessorSingleton.get().get_callback_topic())
        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


@slices.command()
@click.option('--actor', default=None, help='Actor Name', required=True)
@click.option('--sliceid', default=None, help='Slice ID', required=False)
@click.option('--slicename', default=None, help='Slice Name', required=False)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.option('--email', default=None, help='User email', required=False)
@click.option('--states', help="Comma separated list of the states, possible values: "
                               "[nascent, configuring, stableok, stableerror, modifyok, modifyerror, closing, dead]",
              default=None, required=False)
@click.option('--format', default='text', help='Output Format Type: text or json', required=False)
@click.pass_context
def query(ctx, actor, sliceid, slicename, idtoken, refreshtoken, email, states, format):
    """ Get slice(s) from an actor
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ShowCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.get_slices(actor_name=actor, callback_topic=KafkaProcessorSingleton.get().get_callback_topic(),
                                slice_id=sliceid, slice_name=slicename, id_token=idtoken, email=email, states=states,
                                format=format)
        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))

@slices.command()
@click.option('--email', help='User Email', required=True)
@click.option('--actor', help='Actor Name', required=True)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def removealldead(ctx, email, actor, idtoken, refreshtoken):
    """ Removes slice for an actor
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ManageCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.delete_dead_slices(email=email, actor_name=actor, id_token=idtoken,
                                        callback_topic=KafkaProcessorSingleton.get().get_callback_topic())
        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))

@click.group()
@click.pass_context
def slivers(ctx):
    """ Sliver management
    """
    config = os.getenv('FABRIC_MGMT_CLI_CONFIG_PATH')
    if config is None or config == "":
        ctx.fail('FABRIC_MGMT_CLI_CONFIG_PATH is not set')

    return


@slivers.command()
@click.option('--sliverid', help='Sliver Id', required=True)
@click.option('--actor', help='Actor Name', required=True)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def close(ctx, sliverid, actor, idtoken, refreshtoken):
    """ Closes sliver for an actor
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ManageCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.close_reservation(rid=sliverid, actor_name=actor,
                                       callback_topic=KafkaProcessorSingleton.get().get_callback_topic(), id_token=idtoken)
        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


@slivers.command()
@click.option('--sliverid', help='Sliver Id', required=True)
@click.option('--actor', help='Actor Name', required=True)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def remove(ctx, sliverid, actor, idtoken, refreshtoken):
    """ Removes sliver for an actor
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ManageCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.remove_reservation(rid=sliverid, actor_name=actor,
                                        callback_topic=KafkaProcessorSingleton.get().get_callback_topic(), id_token=idtoken)
        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


@slivers.command()
@click.option('--actor', help='Actor Name', required=True)
@click.option('--sliceid', default=None, help='Slice Id', required=False)
@click.option('--sliverid', default=None, help='Sliver Id', required=False)
@click.option('--states', default=None, help='Sliver State, Comma separated list of states, possible values: '
                                             '[nascent, ticketed, active, activeticketed, closed, closewait, '
                                             'failed, unknown, all]', required=False)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.option('--email', default=None, help='User Email', required=False)
@click.option('--site', default=None, help='Site Name', required=False)
@click.option('--type', default=None,
              help='Sliver Type, possible allowed values: '
                   '[VM, L2Bridge, L2STS, L2PTP, FABNetv4, FABNetv6, FABNetv4Ext, FABNetv6Ext, PortMirror, Facility, '
                   'L3VPN]',
              required=False)
@click.option('--format', default='text', help='Output Format Type: text or json', required=False)
@click.option('--fields', default=None, help='Comma separated list of fields to be displayed', required=False)
@click.pass_context
def query(ctx, actor, sliceid, sliverid, states, idtoken, refreshtoken, email, site, type, format, fields):
    """ Get sliver(s) from an actor
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ShowCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.get_reservations(actor_name=actor,
                                      callback_topic=KafkaProcessorSingleton.get().get_callback_topic(),
                                      slice_id=sliceid, rid=sliverid, states=states, id_token=idtoken, email=email,
                                      site=site, type=type, format=format, fields=fields)
        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


@click.group()
@click.pass_context
def delegations(ctx):
    """ Delegation management
    """
    config = os.getenv('FABRIC_MGMT_CLI_CONFIG_PATH')
    if config is None or config == "":
        ctx.fail('FABRIC_MGMT_CLI_CONFIG_PATH is not set')

    return


@delegations.command()
@click.option('--broker', help='Broker Name', required=True)
@click.option('--am', help='AM Name', required=True)
@click.option('--did', default=None, help='Delegation Id', required=False)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def claim(ctx, broker: str, am: str, did: str, idtoken, refreshtoken):
    """ Claim delegation(s) from AM to Broker
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ManageCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.claim_delegations(broker=broker, am=am,
                                       callback_topic=KafkaProcessorSingleton.get().get_callback_topic(),
                                       did=did, id_token=idtoken)
        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


@delegations.command()
@click.option('--broker', help='Broker Name', required=True)
@click.option('--am', help='AM Name', required=True)
@click.option('--did', default=None, help='Delegation Id', required=False)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def reclaim(ctx, broker: str, am: str, did: str, idtoken, refreshtoken):
    """ Reclaim delegation(s) from Broker to AM
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ManageCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.reclaim_delegations(broker=broker, am=am,
                                         callback_topic=KafkaProcessorSingleton.get().get_callback_topic(),
                                         did=did, id_token=idtoken)
        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


@delegations.command()
@click.option('--actor', help='Actor Name', required=True)
@click.option('--sliceid', default=None, help='Slice Id', required=False)
@click.option('--did', default=None, help='Delegation Id', required=False)
@click.option('--states',
              default=None, help="Comma separated list of the states, possible values: "
                                 "[nascent, delegated, reclaimed, failed, closed]",
              required=False)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.option('--format', default='text', help='Output Format Type: text or json', required=False)
@click.pass_context
def query(ctx, actor, sliceid, did, states, idtoken, refreshtoken, format):
    """ Get delegation(s) from an actor
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ShowCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.get_delegations(actor_name=actor,
                                     callback_topic=KafkaProcessorSingleton.get().get_callback_topic(),
                                     slice_id=sliceid, did=did, states=states, id_token=idtoken, format=format)
        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


@delegations.command()
@click.option('--did', help='Delegation Id', required=True)
@click.option('--actor', help='Actor Name', required=True)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def close(ctx, did, actor, idtoken, refreshtoken):
    """ Closes delegation for an actor
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ManageCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.close_delegation(did=did, actor_name=actor,
                                      callback_topic=KafkaProcessorSingleton.get().get_callback_topic(),
                                      id_token=idtoken)
        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


@delegations.command()
@click.option('--did', help='Delegation Id', required=True)
@click.option('--actor', help='Actor Name', required=True)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def remove(ctx, did, actor, idtoken, refreshtoken):
    """ Removes sliver for an actor
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ManageCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.remove_delegation(did=did, actor_name=actor,
                                       callback_topic=KafkaProcessorSingleton.get().get_callback_topic(),
                                       id_token=idtoken)
        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


@click.group()
@click.pass_context
def maintenance(ctx):
    """ Maintenance Operations
    """
    config = os.getenv('FABRIC_MGMT_CLI_CONFIG_PATH')
    if config is None or config == "":
        ctx.fail('FABRIC_MGMT_CLI_CONFIG_PATH is not set')

    return


@maintenance.command()
@click.option('--actor', help='Actor Name', required=True)
@click.option('--mode', help='Mode value, i.e. PreMaint, Maint, Active', required=True)
@click.option('--projects', help='Comma separated list of Project Ids allowed to use TestBed in Maintenance mode',
              required=False, default=None)
@click.option('--users', help='Comma separated list of User emails allowed to use TestBed in Maintenance mode',
              required=False, default=None)
@click.option('--deadline',
              help='Start time that allows new resources to be created or extended up '
                   'until stated deadline in format: %Y-%m-%d %H:%M:%S %z',
              required=False, default=None)
@click.option('--end',
              help='Expected End for the Maintainenance in formt: %Y-%m-%d %H:%M:%S %z',
              required=False, default=None)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def testbed(ctx, actor: str, mode: str, projects: str, users: str, deadline: str, end: str, idtoken: str,
            refreshtoken: str):
    """ Change Maintenance modes (PreMaint, Maint, Active) for the Testbed
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ManageCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.toggle_maintenance_mode(actor_name=actor,
                                             callback_topic=KafkaProcessorSingleton.get().get_callback_topic(),
                                             state=mode, projects=projects, users=users, id_token=idtoken,
                                             deadline=deadline, expected_end=end)
        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


@maintenance.command()
@click.option('--actor', help='Actor Name', required=True)
@click.option('--name', help='Site Name', required=True)
@click.option('--mode', help='Mode value, i.e. PreMaint, Maint, Active', required=True)
@click.option('--projects', help='Comma separated list of Project Ids allowed to use TestBed in Maintenance mode',
              required=False, default=None)
@click.option('--users', help='Comma separated list of User emails allowed to use TestBed in Maintenance mode',
              required=False, default=None)
@click.option('--workers', help='Comma separated list of workers to be marked in Maintenance mode',
              required=False, default=None)
@click.option('--deadline',
              help='Start time that allows new resources to be created or extended up '
                   'until stated deadline in format: %Y-%m-%d %H:%M:%S %z',
              required=False, default=None)
@click.option('--end',
              help='Expected End for the Maintainenance in formt: %Y-%m-%d %H:%M:%S %z',
              required=False, default=None)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def site(ctx, actor: str, name: str, mode: str, projects, users, workers: str, deadline: str, end: str,
         idtoken: str, refreshtoken: str):
    """ Change Maintenance modes (PreMaint, Maint, Active) for a specific Site or a specific worker
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ManageCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.toggle_maintenance_mode(actor_name=actor,
                                             callback_topic=KafkaProcessorSingleton.get().get_callback_topic(),
                                             state=mode, projects=projects, users=users, expected_end=end,
                                             site_name=name, workers=workers, deadline=deadline, id_token=idtoken)

        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))

@maintenance.command()
@click.option('--actor', help='Actor Name', required=True)
@click.option('--sites', help='Site Names, Comma separated list of the site names or ALL for entire testbed', required=False)
@click.pass_context
def query(ctx, actor: str, sites: str):
    """ Query Maintenance Status for Testbed/Site
    """
    try:
        idtoken = KafkaProcessorSingleton.get().start(ignore_tokens=True)
        mgmt_command = ShowCommand(logger=KafkaProcessorSingleton.get().logger)
        mgmt_command.get_sites(actor_name=actor,
                               callback_topic=KafkaProcessorSingleton.get().get_callback_topic(),
                               sites=sites)

        KafkaProcessorSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


managecli.add_command(slices)
managecli.add_command(slivers)
managecli.add_command(delegations)
managecli.add_command(maintenance)
managecli.add_command(netcommands.net)
