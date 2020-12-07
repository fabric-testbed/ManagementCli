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
import logging
import threading
import traceback
import os
from logging.handlers import RotatingFileHandler

import click

from fabric.actor.core.apis.i_actor import ActorType
from fabric.actor.core.manage.kafka.kafka_actor import KafkaActor
from fabric.actor.core.manage.kafka.kafka_broker import KafkaBroker
from fabric.actor.core.manage.kafka.kafka_mgmt_message_processor import KafkaMgmtMessageProcessor
from fabric.actor.core.util.id import ID
from fabric.managecli.config_processor import ConfigProcessor
from fabric.managecli.manage_command import ManageCommand
from fabric.managecli.show_command import ShowCommand


from fabric.managecli.tokens import CredentialManager, TokenException


class MainShell:
    PATH = os.environ.get('FABRIC_MGMT_CLI_CONFIG_PATH', './config.yml')

    def __init__(self):
        self.config_processor = ConfigProcessor(path=self.PATH)
        self.message_processor = None
        self.actor_cache = {}
        self.lock = threading.Lock()
        self.auth = None
        self.logger = None
        self.key_schema = None
        self.val_schema = None
        self.producer = None

    def setup_kafka(self):
        conf = self.config_processor.get_kafka_config_producer()
        key_schema, val_schema = self.config_processor.get_kafka_schemas()
        self.key_schema = key_schema
        self.val_schema = val_schema

        from fabric.message_bus.producer import AvroProducerApi
        self.producer = AvroProducerApi(conf=conf, key_schema=key_schema, record_schema=val_schema, logger=self.logger)

        consumer_conf = self.config_processor.get_kafka_config_consumer()
        topics = [self.config_processor.get_kafka_topic()]

        self.message_processor = KafkaMgmtMessageProcessor(conf=consumer_conf, key_schema=self.key_schema,
                                                           record_schema=self.val_schema, topics=topics,
                                                           logger=self.logger)

    def initialize(self):
        self.config_processor.process()

        self.logger = self.make_logger()

        self.setup_kafka()

        self.load_actor_cache()

    def load_actor_cache(self):
        peers = self.config_processor.get_peers()
        if peers is not None:
            for p in peers:
                mgmt_actor = None
                if p.get_type().lower() == ActorType.Broker.name.lower():
                    mgmt_actor = KafkaBroker(guid=ID(uid=p.get_guid()), kafka_topic=p.get_kafka_topic(),
                                             auth=self.config_processor.get_auth(),
                                             logger=self.logger, message_processor=self.message_processor,
                                             producer=self.producer)
                else:
                    mgmt_actor = KafkaActor(guid=ID(uid=p.get_guid()), kafka_topic=p.get_kafka_topic(),
                                            auth=self.config_processor.get_auth(),
                                            logger=self.logger, message_processor=self.message_processor,
                                            producer=self.producer)
                try:
                    self.lock.acquire()
                    self.logger.debug("Added actor {} to cache".format(p.get_name()))
                    self.actor_cache[p.get_name()] = mgmt_actor
                finally:
                    self.lock.release()
        else:
            self.logger.debug("No peers available")

    def get_mgmt_actor(self, *, name: str) -> KafkaActor:

        try:
            self.lock.acquire()
            return self.actor_cache.get(name, None)
        finally:
            self.lock.release()

    def make_logger(self):
        """
        Detects the path and level for the log file from the actor config and sets
        up a logger. Instead of detecting the path and/or level from the
        config, a custom path and/or level for the log file can be passed as
        optional arguments.

        :param log_path: Path to custom log file
        :param log_level: Custom log level
        :return: logging.Logger object
        """

        # Get the log path
        if self.config_processor is None:
            raise RuntimeError('No config information available')

        log_path = self.config_processor.get_log_dir() + '/' + self.config_processor.get_log_file()

        if log_path is None:
            raise RuntimeError('The log file path must be specified in config or passed as an argument')

        # Get the log level
        log_level = self.config_processor.get_log_level()
        if log_level is None:
            log_level = logging.INFO

        # Set up the root logger
        log = logging.getLogger(self.config_processor.get_log_name())
        log.setLevel(log_level)
        log_format = \
            '%(asctime)s - %(name)s - {%(filename)s:%(lineno)d} - [%(threadName)s] - %(levelname)s - %(message)s'

        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        backup_count = self.config_processor.get_log_retain()
        max_log_size = self.config_processor.get_log_size()

        file_handler = RotatingFileHandler(log_path, backupCount=int(backup_count), maxBytes=int(max_log_size))

        logging.basicConfig(handlers=[file_handler], format=log_format)

        return log

    def get_callback_topic(self) -> str:
        return self.config_processor.get_kafka_topic()

    def get_tokens(self, id_token: str, refresh_token: str) -> str:
        tokens = None
        if refresh_token is None:
            refresh_token = os.getenv('FABRIC_REFRESH_TOKEN', None)

        if refresh_token is not None:
            try:
                tokens = CredentialManager.get_token(refresh_token=refresh_token,
                                                     host=self.config_processor.get_credmgr_host())
                id_token = tokens.get('id_token', None)
            except Exception as e:
                raise TokenException('Not a valid refresh_token! Error: {}'.format(e))

        if id_token is None:
            id_token = os.getenv('FABRIC_ID_TOKEN', None)
            raise TokenException('Either id_token or refresh_token must be specified! Alternatively, '
                                 'set the environment variables FABRIC_ID_TOKEN and FABRIC_REFRESH_TOKEN')

        return id_token

    def start(self, id_token: str, refresh_token: str, ignore_tokens: bool = False) -> str:
        try:
            self.initialize()
            ret_val = None
            if not ignore_tokens:
                ret_val = self.get_tokens(id_token=id_token, refresh_token=refresh_token)
            self.message_processor.start()
            return ret_val
        except TokenException as e:
            err_str = traceback.format_exc()
            self.logger.error(err_str)
            self.logger.debug("Failed to start Management Shell: {}".format(str(e)))
            raise e
        except Exception as e:
            err_str = traceback.format_exc()
            self.logger.error(err_str)
            self.logger.debug("Failed to start Management Shell: {}".format(str(e)))
            raise e

    def stop(self):
        try:
            self.message_processor.stop()
        except Exception as e:
            err_str = traceback.format_exc()
            self.logger.error(err_str)
            self.logger.debug("Failed to stop Management Shell: {}".format(str(e)))


class MainShellSingleton:
    __instance = None

    def __init__(self):
        if self.__instance is not None:
            raise Exception("Singleton can't be created twice !")

    def get(self):
        """
        Actually create an instance
        """
        if self.__instance is None:
            self.__instance = MainShell()
        return self.__instance

    get = classmethod(get)


@click.group()
@click.option('-v', '--verbose', is_flag=True)
@click.pass_context
def managecli(ctx, verbose):
    ctx.ensure_object(dict)
    ctx.obj['VERBOSE'] = verbose


@click.group()
@click.pass_context
def manage(ctx):
    """ issue management commands
    """
    config = os.getenv('FABRIC_MGMT_CLI_CONFIG_PATH')
    if config is None or config == "":
        ctx.fail('FABRIC_MGMT_CLI_CONFIG_PATH is not set')

    return


@manage.command()
@click.option('--broker', default=None, help='Broker Name', required=True)
@click.option('--am', default=None, help='AM Name', required=True)
@click.option('--rid', default=None, help='Reservation Id', required=False)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def claim(ctx, broker: str, am: str, rid: str, idtoken, refreshtoken):
    """ Claim reservations for am to broker
    """
    try:
        idtoken = MainShellSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken)
        mgmt_command = ManageCommand(logger=MainShellSingleton.get().logger)
        mgmt_command.claim_resources(broker=broker, am=am,
                                     callback_topic=MainShellSingleton.get().get_callback_topic(),
                                     rid=rid, id_token=idtoken)
        MainShellSingleton.get().stop()
    except Exception as e:
        #traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


@manage.command()
@click.option('--broker', default=None, help='Broker Name', required=True)
@click.option('--am', default=None, help='AM Name', required=True)
@click.option('--rid', default=None, help='Reservation Id', required=False)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def reclaim(ctx, broker: str, am: str, rid: str, idtoken, refreshtoken):
    """ Claim reservations for am to broker
    """
    try:
        idtoken = MainShellSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken)
        mgmt_command = ManageCommand(logger=MainShellSingleton.get().logger)
        mgmt_command.reclaim_resources(broker=broker, am=am,
                                       callback_topic=MainShellSingleton.get().get_callback_topic(),
                                       rid=rid, id_token=idtoken)
        MainShellSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))

@manage.command()
@click.option('--broker', default=None, help='Broker Name', required=True)
@click.option('--am', default=None, help='AM Name', required=True)
@click.option('--did', default=None, help='Delegation Id', required=False)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def claimdelegation(ctx, broker: str, am: str, did: str, idtoken, refreshtoken):
    """ Claim reservations for am to broker
    """
    try:
        idtoken = MainShellSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ManageCommand(logger=MainShellSingleton.get().logger)
        mgmt_command.claim_delegations(broker=broker, am=am,
                                       callback_topic=MainShellSingleton.get().get_callback_topic(),
                                       did=did, id_token=idtoken)
        MainShellSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))

@manage.command()
@click.option('--broker', default=None, help='Broker Name', required=True)
@click.option('--am', default=None, help='AM Name', required=True)
@click.option('--did', default=None, help='Delegation Id', required=False)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def reclaimdelegation(ctx, broker: str, am: str, did: str, idtoken, refreshtoken):
    """ Claim reservations for am to broker
    """
    try:
        idtoken = MainShellSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken)
        mgmt_command = ManageCommand(logger=MainShellSingleton.get().logger)
        mgmt_command.reclaim_delegations(broker=broker, am=am,
                                         callback_topic=MainShellSingleton.get().get_callback_topic(),
                                         did=did, id_token=idtoken)
        MainShellSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))

@manage.command()
@click.option('--rid', default=None, help='Reservation Id', required=True)
@click.option('--actor', default=None, help='Actor Name', required=True)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def closereservation(ctx, rid, actor, idtoken, refreshtoken):
    """ Closes reservation for an actor
    """
    try:
        idtoken = MainShellSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken)
        mgmt_command = ManageCommand(logger=MainShellSingleton.get().logger)
        mgmt_command.close_reservation(rid=rid, actor_name=actor,
                                       callback_topic=MainShellSingleton.get().get_callback_topic(), id_token=idtoken)
        MainShellSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))

@manage.command()
@click.option('--sliceid', default=None, help='Slice Id', required=True)
@click.option('--actor', default=None, help='Actor Name', required=True)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def closeslice(ctx, sliceid, actor, idtoken, refreshtoken):
    """ Closes Slice for an actor
    """
    try:
        idtoken = MainShellSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken)
        mgmt_command = ManageCommand(logger=MainShellSingleton.get().logger)
        mgmt_command.close_slice(slice_id=sliceid, actor_name=actor,
                                 callback_topic=MainShellSingleton.get().get_callback_topic(), id_token=idtoken)
        MainShellSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


@manage.command()
@click.option('--rid', default=None, help='Reservation Id', required=True)
@click.option('--actor', default=None, help='Actor Name', required=True)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def removereservation(ctx, rid, actor, idtoken, refreshtoken):
    """ Removes reservation for an actor
    """
    try:
        idtoken = MainShellSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken)
        mgmt_command = ManageCommand(logger=MainShellSingleton.get().logger)
        mgmt_command.remove_reservation(rid=rid, actor_name=actor,
                                        callback_topic=MainShellSingleton.get().get_callback_topic(), id_token=idtoken)
        MainShellSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))


@manage.command()
@click.option('--sliceid', default=None, help='Slice Id', required=True)
@click.option('--actor', default=None, help='Actor Name', required=True)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def removeslice(ctx, sliceid, actor, idtoken, refreshtoken):
    """ Removes slice for an actor
    """
    try:
        idtoken = MainShellSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken)
        mgmt_command = ManageCommand(logger=MainShellSingleton.get().logger)
        mgmt_command.remove_slice(slice_id=sliceid, actor_name=actor,
                                  callback_topic=MainShellSingleton.get().get_callback_topic(), id_token=idtoken)
        MainShellSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))

@click.group()
@click.pass_context
def show(ctx):
    """ issue show commands
    """
    config = os.getenv('FABRIC_MGMT_CLI_CONFIG_PATH')
    if config is None or config == "":
        ctx.fail('FABRIC_MGMT_CLI_CONFIG_PATH is not set')
    return


@show.command()
@click.option('--actor', default=None, help='Actor Name', required=True)
@click.option('--sliceid', default=None, help='Slice ID', required=False)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def slices(ctx, actor, sliceid, idtoken, refreshtoken):
    """ Get Slices from an actor
    """
    try:
        idtoken = MainShellSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ShowCommand(logger=MainShellSingleton.get().logger)
        mgmt_command.get_slices(actor_name=actor, callback_topic=MainShellSingleton.get().get_callback_topic(),
                                slice_id=sliceid, id_token=idtoken)
        MainShellSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))



@show.command()
@click.option('--actor', default=None, help='Actor Name', required=True)
@click.option('--rid', default=None, help='Reservation Id', required=False)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def reservations(ctx, actor, rid, idtoken, refreshtoken):
    """ Get Slices from an actor
    """
    try:
        idtoken = MainShellSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken)
        mgmt_command = ShowCommand(logger=MainShellSingleton.get().logger)
        mgmt_command.get_reservations(actor_name=actor, callback_topic=MainShellSingleton.get().get_callback_topic(),
                                      rid=rid, id_token=idtoken)
        MainShellSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))

@show.command()
@click.option('--actor', default=None, help='Actor Name', required=True)
@click.option('--did', default=None, help='Delegation Id', required=False)
@click.option('--idtoken', default=None, help='Fabric Identity Token', required=False)
@click.option('--refreshtoken', default=None, help='Fabric Refresh Token', required=False)
@click.pass_context
def delegations(ctx, actor, did, idtoken, refreshtoken):
    """ Get Slices from an actor
    """
    try:
        idtoken = MainShellSingleton.get().start(id_token=idtoken, refresh_token=refreshtoken, ignore_tokens=True)
        mgmt_command = ShowCommand(logger=MainShellSingleton.get().logger)
        mgmt_command.get_delegations(actor_name=actor, callback_topic=MainShellSingleton.get().get_callback_topic(),
                                     did=did, id_token=idtoken)
        MainShellSingleton.get().stop()
    except Exception as e:
        # traceback.print_exc()
        click.echo('Error occurred: {}'.format(e))

managecli.add_command(manage)
managecli.add_command(show)
