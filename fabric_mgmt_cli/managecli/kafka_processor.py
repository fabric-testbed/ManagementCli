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
import os
import threading
import traceback
from logging.handlers import RotatingFileHandler

from fabric_cf.actor.core.apis.abc_actor_mixin import ActorType
from fabric_cf.actor.core.manage.kafka.kafka_actor import KafkaActor
from fabric_cf.actor.core.manage.kafka.kafka_broker import KafkaBroker
from fabric_cf.actor.core.manage.kafka.kafka_mgmt_message_processor import KafkaMgmtMessageProcessor
from fabric_cf.actor.core.util.id import ID
from fabric_cm.credmgr.credmgr_proxy import CredmgrProxy

from fabric_mgmt_cli.managecli.config_processor import ConfigProcessor


class TokenException(Exception):
    pass


class KafkaProcessor:
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
        """
        Set up Kafka Producer and Consumer
        """
        conf = self.config_processor.get_kafka_config_producer()
        self.key_schema = self.config_processor.get_kafka_key_schema()
        self.val_schema = self.config_processor.get_kafka_value_schema()

        from fabric_mb.message_bus.producer import AvroProducerApi
        self.producer = AvroProducerApi(producer_conf=conf, key_schema_location=self.key_schema,
                                        value_schema_location=self.val_schema, logger=self.logger)

        consumer_conf = self.config_processor.get_kafka_config_consumer()
        topics = [self.config_processor.get_kafka_topic()]

        self.message_processor = KafkaMgmtMessageProcessor(consumer_conf=consumer_conf,
                                                           key_schema_location=self.key_schema,
                                                           value_schema_location=self.val_schema, topics=topics,
                                                           logger=self.logger)

    def initialize(self):
        """
        Initialize the Kafka Processor
        """
        self.config_processor.process()

        self.logger = self.make_logger()

        self.setup_kafka()

        self.load_actor_cache()

    def load_actor_cache(self):
        """
        Load the Actor Cache
        """
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
        """
        Get Management Actor from Cache
        @param name actor name
        @return Management Actor
        """

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
        """
        Get Callback Topic
        @return callback topic
        """
        return self.config_processor.get_kafka_topic()

    def get_tokens(self, id_token: str, refresh_token: str) -> str:
        """
        Get Tokens
        @param id_token id token
        @param refresh_token refresh token
        @return Fabric Identity Token
        """
        tokens = None
        if refresh_token is None:
            refresh_token = os.getenv('FABRIC_REFRESH_TOKEN', None)

        if refresh_token is not None:
            try:
                proxy = CredmgrProxy(credmgr_host=self.config_processor.get_credmgr_host())
                tokens = proxy.refresh(project_id=None, scope="all", refresh_token=refresh_token)
                id_token = tokens.get('id_token', None)
            except Exception as e:
                raise TokenException('Not a valid refresh_token! Error: {}'.format(e))

        if id_token is None:
            id_token = os.getenv('FABRIC_ID_TOKEN', None)
            raise TokenException('Either id_token or refresh_token must be specified! Alternatively, '
                                 'set the environment variables FABRIC_ID_TOKEN and FABRIC_REFRESH_TOKEN')

        return id_token

    def start(self, id_token: str = None, refresh_token: str = None, ignore_tokens: bool = False) -> str:
        """
        Start Synchronous Kafka Processor
        @param id_token identity token
        @param refresh_token refresh token
        @param ignore_tokens flag  to indicate to ignore tokens
        @return token if ignore_tokens is False; None otherwise
        """
        try:
            self.initialize()
            ret_val = None
            if not ignore_tokens:
                ret_val = self.get_tokens(id_token=id_token, refresh_token=refresh_token)
            self.message_processor.start()
            return ret_val
        except TokenException as e:
            self.logger.debug(f"Failed to start Management Shell: {e}")
            self.logger.error(traceback.format_exc())
            raise e
        except Exception as e:
            self.logger.debug(f"Failed to start Management Shell: {e}")
            self.logger.error(traceback.format_exc())
            raise e

    def stop(self):
        """
        Stop the Synchronous Kafka Processor
        """
        try:
            self.message_processor.stop()
        except Exception as e:
            self.logger.debug(f"Failed to stop Management Shell: {e}")
            self.logger.error(traceback.format_exc())


class KafkaProcessorSingleton:
    """
    Kafka Processor Singleton
    """
    __instance = None

    def __init__(self):
        if self.__instance is not None:
            raise Exception("Singleton can't be created twice !")

    def get(self):
        """
        Actually create an instance
        """
        if self.__instance is None:
            self.__instance = KafkaProcessor()
        return self.__instance

    get = classmethod(get)
