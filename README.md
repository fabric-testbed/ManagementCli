[![Requirements Status](https://requires.io/github/fabric-testbed/ManagementCli/requirements.svg?branch=main)](https://requires.io/github/fabric-testbed/ManagementCli/requirements/?branch=main)

[![PyPI](https://img.shields.io/pypi/v/fabric-mgmt-cli?style=plastic)](https://pypi.org/project/fabric-mgmt-cli/)

# ManagementCli
Fabric Control Framework Management CLI for administrative operations over Kafka

## Overview
Management CLI talks to various CF components over Kafka to query and perform various administrative operations.
Below is the list of the operations supported so far

Command | SubCommand | Action | Input | Output
:--------|:----:|:----:|:---:|:---:
`manage` | `claimdelegeation`| Claim Delegation(s) from AM by Broker | `broker` Broker, `am` Aggregate Manager, `did` [Delegation Id] | Delegation Id of delegation claimed
`manage` | `reclaimdelegeation`| Reclaim Delegation(s) from AM by Broker | `broker` Broker, `am` Aggregate Manager, `did` [Delegation Id] | Delegation Id of delegation reclaimed
`manage` | `closeslice` | Close Slice for a CF Actor |  `actor` Actor, `sliceid` [Slice Id] | Success or Failure status
`manage` | `closereservation` | Close Reservation for a CF Actor |  `actor` Actor, `rid` [Reservation Id] | Success or Failure status
`manage` | `removeslice` | Remove Slice for a CF Actor |  `actor` Actor, `sliceid` [Slice Id] | Success or Failure status
`manage` | `removereservation` | Remove Reservation for a CF Actor |  `actor` Actor, `rid` [Reservation Id] | Success or Failure status
`show` | `slices`| Show Slice(s) for a CF Actor | `actor` Actor, `sliceid` [Slice Id] | Slices for an actor or Slice identified by Slice Id
`show` | `reservations`| Show Reservation(s) for a CF Actor | `actor` Actor, `rid` [Reservation Id] | Reservations for an actor or Reservation identified by Reservation Id
`show` | `delegations`| Show Delegation(s) for a CF Actor | `actor` Actor, `did` [Delegation Id] | Delegations for an actor or Delegation identified by Delegation Id

## Requirements
Python 3.7+

## Pre-requisites
Ensure that following are installed
- `virtualenv`
- `virtualenvwrapper`

## Installation
Multiple installation options possible. For CF development the recommended method is to install from GitHub MASTER branch:
```
$ mkvirtualenv mgmtcli
$ workon mgmtcli
$ pip install git+https://github.com/fabric-testbed/ManagementCli.git
```
For inclusion in tools, etc, use PyPi
```
$ mkvirtualenv mgmtcli
$ workon mgmtcli
$ pip install fabric-mgmt-cli
```
## Configuration
Management CLI expects the user to set `FABRIC_MGMT_CLI_CONFIG_PATH` environment variable from where `config.yml` to be picked. 
If the environment variable is not set, it will try to look for `config.yml` in users home directory.

In addition, User is expected to pass either Fabric Identity Token or Fabric Refresh Token to all the commands. 
Alternatively, user is expected to set atleast one of the environment variables `FABRIC_ID_TOKEN` and `FABRIC_REFRESH_TOKEN`.

Create config.yml with default content as shown below. 

User is expected to update the following parameters:
 - Kafka Cluster Parameters
 - CF Peers with Kafka topics 
 - Log File Location

```
runtime:
  - kafka-topic: managecli-topic
  - kafka-server: broker1:9092
  - kafka-schema-registry-url: http://schemaregistry:8081
  - kafka-key-schema: /etc/fabric/message_bus/schema/key.avsc
  - kafka-value-schema: /etc/fabric/message_bus/schema/message.avsc
  - kafka-ssl-ca-location:  /etc/fabric/message_bus/ssl/cacert.pem
  - kafka-ssl-certificate-location:  /etc/fabric/message_bus/ssl/client.pem
  - kafka-ssl-key-location:  /etc/fabric/message_bus/ssl/client.key
  - kafka-ssl-key-password:  fabric
  - kafka-security-protocol: SSL
  - kafka-group-id: fabric-cf
  - kafka-sasl-mechanism:
  - kafka-sasl-producer-username:
  - kafka-sasl-producer-password:
  - kafka-sasl-consumer-username:
  - kafka-sasl-consumer-password:

logging:
  ## The directory in which actor should create log files.
  ## This directory will be automatically created if it does not exist.
  - log-directory: /var/log/managecli

  ## The filename to be used for actor's log file.
  - log-file: manage.log

  ## The default log level for actor.
  - log-level: DEBUG

  ## actor rotates log files. You may specify how many archived log files to keep here.
  - log-retain: 5

  ## actor rotates log files after they exceed a certain size.
  ## You may specify the file size that results in a log file being rotated here.
  - log-size: 5000000

  - logger: managecli
auth:
  - name: managecli
  - guid: managecli-guid
  - credmgr-host: https://dev-2.fabric_mgmt_cli-testbed.net/

peers:
  - peer:
    - name: orchestrator
    - type: orchestrator
    - guid: orchestrator-guid
    - kafka-topic: orchestrator-topic
  - peer:
    - name: net1-am
    - guid: net1-am-guid
    - type: authority
    - kafka-topic: net1-am-topic
  - peer:
    - name: site1-am
    - guid: site1-am-guid
    - type: authority
    - kafka-topic: site1-am-topic
  - peer:
      - name: broker
      - guid: broker-guid
      - type: broker
      - kafka-topic: broker-topic
```

## Usage
Management CLI supports show and manage commands:
```
(mgmtcli) $ fabric-mgmt-cli
Usage: fabric-mgmt-cli [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose
  --help         Show this message and exit.

Commands:
  delegations  Delegation management
  slices       Slice management
  slivers      Sliver management
```
### Delegation Commands
List of the delegation commands supported can be found below:
```
(mgmtcli) $ fabric-mgmt-cli delegations
Usage: fabric-mgmt-cli delegations [OPTIONS] COMMAND [ARGS]...

  Delegation management

Options:
  --help  Show this message and exit.

Commands:
  claim    Claim delegation(s) from AM to Broker
  query    Get delegation(s) from an actor
  reclaim  Reclaim delegation(s) from Broker to AM
```
### Slice Commands
List of the Slice commands supported can be found below:
```
(mgmtcli) $ fabric-mgmt-cli slices
Usage: fabric-mgmt-cli slices [OPTIONS] COMMAND [ARGS]...

  Slice management

Options:
  --help  Show this message and exit.

Commands:
  close   Closes slice for an actor
  query   Get slice(s) from an actor
  remove  Removes slice for an actor
```
### Sliver Commands
List of the Sliver commands supported can be found below:
```
(mgmtcli) $ fabric-mgmt-cli slivers
Usage: fabric-mgmt-cli slivers [OPTIONS] COMMAND [ARGS]...

  Sliver management

Options:
  --help  Show this message and exit.

Commands:
  close   Closes sliver for an actor
  query   Get sliver(s) from an actor
  remove  Removes sliver for an actor
```