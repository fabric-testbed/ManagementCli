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

## Installation
Multiple installation options possible. For CF development the recommended method is to install from GitHub MASTER branch:

$ pip install git+https://github.com/fabric-testbed/ManagementCli.git

For inclusion in tools, etc, use PyPi

$ pip install fabric-mgmt-cli

## Configuration
Management CLI expects the user to set `FABRIC_MGMT_CLI_CONFIG_PATH` environment variable from where `config.yml` to be picked. If the environment variable is not set, it will try to look for `config.yml` in users home directory. 

User is expected to specify following:
 - Kafka Cluster Parameters
 - CF Peers with Kafka topics 
 - Log File Location

```
runtime:
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

