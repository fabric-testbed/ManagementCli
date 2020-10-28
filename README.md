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
(mgmtcli) [kthare10@dev-3 ~]$ export FABRIC_MGMT_CLI_CONFIG_PATH=~/managecli/config.yml
(mgmtcli) [kthare10@dev-3 ~]$ fabric-mgmt-cli
Usage: fabric-mgmt-cli [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose
  --help         Show this message and exit.

Commands:
  manage  issue management commands
  show    issue show commands
```
### Manage Commands
List of the manage commands supported can be found below:
```
(mgmtcli) [kthare10@dev-3 ManagementCli]$ fabric-mgmt-cli manage
Usage: fabric-mgmt-cli manage [OPTIONS] COMMAND [ARGS]...

  issue management commands

Options:
  --help  Show this message and exit.

Commands:
  claim              Claim reservations for am to broker
  claimdelegation    Claim reservations for am to broker
  closereservation   Closes reservation for an actor
  closeslice         Closes Slice for an actor
  reclaim            Claim reservations for am to broker
  reclaimdelegation  Claim reservations for am to broker
  removereservation  Removes reservation for an actor
  removeslice        Removes slice for an actor
```
#### Example
Below is an example of `claimdelegation`
```
(mgmtcli) [kthare10@dev-3 ~]$ fabric-mgmt-cli manage claimdelegation --broker broker --am site1-am
Claiming Delegation# 93758341-5053-47a5-b1fc-0b19c8d4f609
Delegation claimed: 93758341-5053-47a5-b1fc-0b19c8d4f609
```
### Show Commands
List of the show commands supported can be found below:
```
(mgmtcli) [kthare10@dev-3 ManagementCli]$ fabric-mgmt-cli show
Usage: fabric-mgmt-cli show [OPTIONS] COMMAND [ARGS]...

  issue management commands

Options:
  --help  Show this message and exit.

Commands:
  delegations   Get Slices from an actor
  reservations  Get Slices from an actor
  slices        Get Slices from an actor
```
#### Example
Below is an example of `show delegations`
```
(mgmtcli) [kthare10@dev-3 ManagementCli]$ fabric-mgmt-cli show delegations --actor site1-am

Delegation ID: 93758341-5053-47a5-b1fc-0b19c8d4f609 Slice ID: 0c197b7a-3ed4-4354-bd89-076ab4ba0eac
Sequence: 0
Graph: <?xml version="1.0" encoding="UTF-8"?><graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"><key id="GraphID" for="node" attr.name="GraphID" attr.type="string"/><key id="labels" for="node" attr.name="labels" attr.type="string"/>
<key id="Labels" for="node" attr.name="Labels" attr.type="string"/><key id="label" for="node" attr.name="label" attr.type="string"/><key id="Capacities" for="node" attr.name="Capacities" attr.type="string"/><key id="Layer" for="node" attr.name="Layer" attr.type="string"/><key id="labels" for="node" attr.name="labels" attr.type="string"/><key id="Name" for="node" attr.name="Name" attr.type="string"/><key id="LabelDelegations" for="node" attr.name="LabelDelegations" attr.type="string"/><key id="Type" for="node" attr.name="Type" attr.type="string"/><key id="CapacityDelegations" for="node" attr.name="CapacityDelegations" attr.type="string"/><key id="Model" for="node" attr.name="Model" attr.type="string"/><key id="x" for="node" attr.name="x" attr.type="string"/><key id="NodeID" for="node" attr.name="NodeID" attr.type="string"/><key id="y" for="node" attr.name="y" attr.type="string"/><key id="Class" for="node" attr.name="Class" attr.type="string"/><key id="id" for="node" attr.name="id" attr.type="string"/><key id="label" for="edge" attr.name="label" attr.type="string"/><key id="Class" for="edge" attr.name="Class" attr.type="string"/><key id="id" for="edge" attr.name="id" attr.type="string"/><graph id="G" edgedefault="directed"><node id="n158" labels=":Component:GraphNode"><data key="labels">:Component:GraphNode</data><data key="CapacityDelegations">[{"unit": 1}]</data><data key="Model">RTX3600</data><data key="y">55.62500000000003</data><data key="labels">:Component:GraphNode</data><data key="x">296.0</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Labels">{ "bdf": "00:00.1" }</data><data key="Class">Component</data><data key="Type">GPU</data><data key="label">GPU</data><data key="Capacities">{ "unit": 1 }</data><data key="NodeID">8dcf8360-10ce-413d-8e9d-e9a2d71c897e</data><data key="id">n1</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Name">GPU1</data></node><node id="n159" labels=":Component:GraphNode"><data key="labels">:Component:GraphNode</data><data key="x">345.0</data><data key="CapacityDelegations">[{"unit": 1}]</data><data key="Model">ConnectX-6</data><data key="y">225.62500000000003</data><data key="labels">:Component:GraphNode</data><data key="label">NIC</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Labels">{ "bdf": "00:00.3" }</data><data key="Class">Component</data><data key="Type">SmartNIC</data><data key="Capacities">{ "unit": 1 }</data><data key="NodeID">4797ab66-7dc7-4fe1-8335-549f66f16abc</data><data key="id">n2</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Name">NIC1</data></node><node id="n160" labels=":GraphNode:NetworkNode"><data key="labels">:GraphNode:NetworkNode</data><data key="y">122.12500000000003</data><data key="label">NetworkNode</data><data key="Model">Dell R7525</data><data key="labels">:GraphNode:NetworkNode</data><data key="x">305.0</data><data key="Name">Worker1</data><data key="Type">Server</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">NetworkNode</data><data key="Labels">None</data><data key="CapacityDelegations">[{"unit": 4, "core": 12, "ram": 128, "disk": 1000}]</data><data key="NodeID">2046922a-a8ed-4b60-8190-b6ce614c514d</data><data key="id">n3</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Capacities">{ "unit": 1, "core": 32, "ram": 384, "disk": 3000 }</data></node><node id="n161" labels=":ConnectionPoint:GraphNode"><data key="labels">:ConnectionPoint:GraphNode</data><data key="x">266.0</data><data key="y">392.0</data><data key="Type">Port</data><data key="label">CP</data><data key="Model">100G SR</data><data key="labels">:ConnectionPoint:GraphNode</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">ConnectionPoint</data><data key="CapacityDelegations">None</data><data key="Capacities">{ "bw": 100}</data><data key="Name">p1e1</data><data key="NodeID">df6f1ba9-752e-4ab6-b3ba-161d0b2474f4</data><data key="id">n4</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Labels">None</data></node><node id="n162" labels=":GraphNode:Link"><data key="labels">:GraphNode:Link</data><data key="y">471.25</data><data key="label">Link</data><data key="Model">DAC123</data><data key="x">416.0</data><data key="labels">:GraphNode:Link</data><data key="Type">DAC</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">Link</data><data key="Labels">None</data><data key="Name">None</data><data key="CapacityDelegations">None</data><data key="NodeID">db1b88d8-7c59-4115-a8d5-d818cad5cda9</data><data key="id">n5</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Capacities">None</data></node><node id="n163" labels=":GraphNode:SwitchFabric"><data key="labels">:GraphNode:SwitchFabric</data><data key="x">231.0</data><data key="y">661.0</data><data key="Type">SwitchFabric</data><data key="label">SwitchFabric</data><data key="labels">:GraphNode:SwitchFabric</data><data key="Model">None</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">SwitchFabric</data><data key="Name">SwitchFabric1 </data><data key="Capacities">{ "unit": 1 }</data><data key="CapacityDelegations">None</data><data key="NodeID">fadc6379-ad6b-4fc2-a6ad-6df1072d24ac</data><data key="id">n6</data><data key="Layer">L2</data><data key="LabelDelegations">None</data><data key="Labels">None</data></node><node id="n164" labels=":ConnectionPoint:GraphNode"><data key="labels">:ConnectionPoint:GraphNode</data><data key="x">345.0</data><data key="y">392.0</data><data key="Type">Port</data><data key="label">CP</data><data key="Model">100G SR</data><data key="labels">:ConnectionPoint:GraphNode</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">ConnectionPoint</data><data key="CapacityDelegations">None</data><data key="Capacities">{ "bw": 100}</data><data key="Name">p1e2</data><data key="NodeID">4c678de5-7d29-48e8-81fb-bc603c7b253b</data><data key="id">n7</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Labels">None</data></node><node id="n165" labels=":ConnectionPoint:GraphNode"><data key="labels">:ConnectionPoint:GraphNode</data><data key="x">423.0</data><data key="y">389.0</data><data key="Type">Port</data><data key="label">CP</data><data key="Model">100G SR</data><data key="labels">:ConnectionPoint:GraphNode</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">ConnectionPoint</data><data key="CapacityDelegations">None</data><data key="Capacities">{ "bw": 100}</data><data key="Name">eth0</data><data key="NodeID">6765b878-8568-455c-b21a-714ca6d3153c</data><data key="id">n8</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Labels">None</data></node><node id="n166" labels=":GraphNode:Link"><data key="labels">:GraphNode:Link</data><data key="y">471.25</data><data key="label">Link</data><data key="Model">DAC123</data><data key="x">338.0</data><data key="labels">:GraphNode:Link</data><data key="Type">DAC</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">Link</data><data key="Labels">None</data><data key="Name">None</data><data key="CapacityDelegations">None</data><data key="NodeID">98350264-5b29-4f93-b563-60150f74164e</data><data key="id">n9</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Capacities">None</data></node><node id="n167" labels=":GraphNode:Link"><data key="labels">:GraphNode:Link</data><data key="y">471.25</data><data key="label">Link</data><data key="Model">DAC123</data><data key="x">259.0</data><data key="labels">:GraphNode:Link</data><data key="Type">DAC</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">Link</data><data key="Labels">None</data><data key="Name">None</data><data key="CapacityDelegations">None</data><data key="NodeID">c1546b9f-70c1-4488-a016-85ae4ba0b44a</data><data key="id">n10</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Capacities">None</data></node><node id="n168" labels=":ConnectionPoint:GraphNode"><data key="labels">:ConnectionPoint:GraphNode</data><data key="x">423.0</data><data key="y">542.0</data><data key="Type">Port</data><data key="label">CP</data><data key="Model">100G SR</data><data key="labels">:ConnectionPoint:GraphNode</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">ConnectionPoint</data><data key="CapacityDelegations">None</data><data key="Capacities">{ "bw": 100 }</data><data key="Name">p003</data><data key="NodeID">125b000e-eef3-4b17-95d1-6fbe64885383</data><data key="id">n11</data><data key="Layer">None</data><data key="Labels">None</data><data key="LabelDelegations">[{"ipv4": ["192.168.1.1", "192.168.1.2"], "vlan": ["100", "101", "102"], "label_pool": "pool1"}, {"pool": ["pool1"]}]</data></node><node id="n170" labels=":ConnectionPoint:GraphNode"><data key="labels">:ConnectionPoint:GraphNode</data><data key="x">345.0</data><data key="label">CP</data><data key="Model">100G SR</data><data key="y">543.0</data><data key="labels">:ConnectionPoint:GraphNode</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">ConnectionPoint</data><data key="Type">Port</data><data key="Capacities">{ "bw": 100 }</data><data key="CapacityDelegations">None</data><data key="NodeID">e1789709-47d1-4854-9d55-176fbe6fd53e</data><data key="LabelDelegations">[{"pool": ["pool3"]}]</data><data key="id">n12</data><data key="Layer">None</data><data key="Labels">None</data><data key="Name">p002</data></node><node id="n171" labels=":ConnectionPoint:GraphNode"><data key="labels">:ConnectionPoint:GraphNode</data><data key="x">266.0</data><data key="y">541.0</data><data key="Type">Port</data><data key="label">CP</data><data key="Model">100G SR</data><data key="labels">:ConnectionPoint:GraphNode</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">ConnectionPoint</data><data key="CapacityDelegations">None</data><data key="Capacities">{ "bw": 100 }</data><data key="Name">p001</data><data key="NodeID">ff09ef43-bd62-4560-8faf-ad3d9aa72c94</data><data key="id">n13</data><data key="Layer">None</data><data key="Labels">None</data><data key="LabelDelegations">[{"ipv4": ["192.168.100.1", "192.168.100.2", "192.168.100.3", "192.168.100.4"], "label_pool": "pool3"}, {"pool": ["pool3"]}]</data></node><node id="n172" labels=":GraphNode:NetworkNode"><data key="labels">:GraphNode:NetworkNode</data><data key="label">Switch</data><data key="Model">Cisco NCS55</data><data key="labels">:GraphNode:NetworkNode</data><data key="x">89.5</data><data key="Name">DataplaneSwitch1</data><data key="y">640.5</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">NetworkNode</data><data key="Type">Switch</data><data key="Capacities">{ "unit": 1 }</data><data key="CapacityDelegations">None</data><data key="NodeID">a072e271-beb4-42ab-b95c-fa491d3725a2</data><data key="id">n14</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Labels">None</data></node><node id="n174" labels=":GraphNode:NetworkNode"><data key="labels">:GraphNode:NetworkNode</data><data key="y">123.12500000000003</data><data key="label">NetworkNode</data><data key="Model">Dell R7525</data><data key="labels">:GraphNode:NetworkNode</data><data key="x">545.0</data><data key="Name">Worker2</data><data key="Type">Server</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">NetworkNode</data><data key="Labels">None</data><data key="CapacityDelegations">[{"unit": 4, "core": 12, "ram": 128, "disk": 1000}]</data><data key="NodeID">9c2cf571-f96c-4fb5-a0f6-64ce09a211f0</data><data key="id">n15</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Capacities">{ "unit": 1, "core": 32, "ram": 384, "disk": 3000 }</data></node><node id="n177" labels=":Component:GraphNode"><data key="labels">:Component:GraphNode</data><data key="x">555.0</data><data key="CapacityDelegations">[{"unit": 1}]</data><data key="Model">ConnectX-6</data><data key="y">205.62500000000003</data><data key="labels">:Component:GraphNode</data><data key="label">NIC</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Labels">{ "bdf": "00:00.2" }</data><data key="Class">Component</data><data key="Type">SmartNIC</data><data key="Capacities">{ "unit": 1 }</data><data key="NodeID">a108e602-c204-494e-8f62-e71b35f4fb98</data><data key="id">n17</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Name">NIC1</data></node><node id="n179" labels=":ConnectionPoint:GraphNode"><data key="labels">:ConnectionPoint:GraphNode</data><data key="x">525.0</data><data key="y">390.97222222222223</data><data key="Type">Port</data><data key="label">CP</data><data key="Model">100G SR</data><data key="labels">:ConnectionPoint:GraphNode</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">ConnectionPoint</data><data key="CapacityDelegations">None</data><data key="Capacities">{ "bw": 100}</data><data key="Name">p1e1</data><data key="NodeID">9e6b4d16-acad-43df-a211-394c9f273b32</data><data key="id">n19</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Labels">None</data></node><node id="n180" labels=":ConnectionPoint:GraphNode"><data key="labels">:ConnectionPoint:GraphNode</data><data key="x">585.0</data><data key="y">390.27777777777777</data><data key="Type">Port</data><data key="label">CP</data><data key="Model">100G SR</data><data key="labels">:ConnectionPoint:GraphNode</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">ConnectionPoint</data><data key="CapacityDelegations">None</data><data key="Capacities">{ "bw": 100}</data><data key="Name">p1e2</data><data key="NodeID">73cfcc85-cd7a-4ba6-b2e1-e90e6b240ba6</data><data key="id">n20</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Labels">None</data></node><node id="n184" labels=":ConnectionPoint:GraphNode"><data key="labels">:ConnectionPoint:GraphNode</data><data key="x">784.3055555555555</data><data key="y">392.3611111111111</data><data key="Type">Port</data><data key="label">CP</data><data key="Model">100G SR</data><data key="labels">:ConnectionPoint:GraphNode</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">ConnectionPoint</data><data key="CapacityDelegations">None</data><data key="Capacities">{ "bw": 100}</data><data key="Name">eth0</data><data key="NodeID">11a5cfbc-5b73-428e-aef3-5f7174a2492a</data><data key="id">n23</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Labels">None</data></node><node id="n187" labels=":GraphNode:Link"><data key="labels">:GraphNode:Link</data><data key="y">471.25</data><data key="label">Link</data><data key="Model">DAC123</data><data key="x">518.0</data><data key="labels">:GraphNode:Link</data><data key="Type">DAC</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">Link</data><data key="Labels">None</data><data key="Name">None</data><data key="CapacityDelegations">None</data><data key="NodeID">d4bde49e-2899-4b8e-9f44-0977bb219fdf</data><data key="id">n24</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Capacities">None</data></node><node id="n188" labels=":GraphNode:Link"><data key="labels">:GraphNode:Link</data><data key="y">471.25</data><data key="label">Link</data><data key="Model">DAC123</data><data key="x">578.0</data><data key="labels">:GraphNode:Link</data><data key="Type">DAC</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">Link</data><data key="Labels">None</data><data key="Name">None</data><data key="CapacityDelegations">None</data><data key="NodeID">9438099f-4996-4654-93e1-998401a1e134</data><data key="id">n25</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Capacities">None</data></node><node id="n191" labels=":GraphNode:Link"><data key="labels">:GraphNode:Link</data><data key="y">471.25</data><data key="label">Link</data><data key="Model">DAC123</data><data key="x">777.0</data><data key="labels">:GraphNode:Link</data><data key="Type">DAC</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">Link</data><data key="Labels">None</data><data key="Name">None</data><data key="CapacityDelegations">None</data><data key="NodeID">cb8f21ce-69a1-483c-adaa-66a0e8a27a64</data><data key="id">n28</data><data key="Layer">None</data><data key="LabelDelegations">None</data><data key="Capacities">None</data></node><node id="n192" labels=":ConnectionPoint:GraphNode"><data key="labels">:ConnectionPoint:GraphNode</data><data key="x">525.0</data><data key="label">CP</data><data key="Model">100G SR</data><data key="y">539.0</data><data key="labels">:ConnectionPoint:GraphNode</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">ConnectionPoint</data><data key="Type">Port</data><data key="Capacities">{ "bw": 100 }</data><data key="CapacityDelegations">None</data><data key="NodeID">37835101-73e8-4246-92c5-8716e366bc5a</data><data key="LabelDelegations">[{"pool": ["pool3"]}]</data><data key="id">n29</data><data key="Layer">None</data><data key="Labels">None</data><data key="Name">p004</data></node><node id="n193" labels=":ConnectionPoint:GraphNode"><data key="labels">:ConnectionPoint:GraphNode</data><data key="x">585.0</data><data key="label">CP</data><data key="Model">100G SR</data><data key="y">538.0</data><data key="labels">:ConnectionPoint:GraphNode</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">ConnectionPoint</data><data key="Type">Port</data><data key="Capacities">{ "bw": 100 }</data><data key="CapacityDelegations">None</data><data key="NodeID">9e1cf321-ecf7-4437-afa8-73688ac3c3ff</data><data key="LabelDelegations">[{"pool": ["pool3"]}]</data><data key="id">n30</data><data key="Layer">None</data><data key="Labels">None</data><data key="Name">p005</data></node><node id="n198" labels=":ConnectionPoint:GraphNode"><data key="labels">:ConnectionPoint:GraphNode</data><data key="LabelDelegations">[{"pool": ["pool1"]}]</data><data key="x">784.0</data><data key="y">535.0</data><data key="Type">Port</data><data key="label">CP</data><data key="Model">100G SR</data><data key="labels">:ConnectionPoint:GraphNode</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">ConnectionPoint</data><data key="CapacityDelegations">None</data><data key="Capacities">{ "bw": 100 }</data><data key="Name">p008</data><data key="NodeID">54983b08-c400-405e-a40b-e596a2ea8b6c</data><data key="id">n33</data><data key="Layer">None</data><data key="Labels">None</data></node><node id="n200" labels=":GraphNode:SwitchFabric"><data key="labels">:GraphNode:SwitchFabric</data><data key="x">320.09722222222223</data><data key="label">SwitchFabric</data><data key="y">276.80555555555554</data><data key="labels">:GraphNode:SwitchFabric</data><data key="Name">NICSwitchFabric1</data><data key="Model">None</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">SwitchFabric</data><data key="Type">SwitchFabric</data><data key="Capacities">{ "unit": 1 }</data><data key="CapacityDelegations">None</data><data key="NodeID">12cf268b-a3ec-48ce-9abd-8f7ce4e397a5</data><data key="id">n34</data><data key="Layer">L2</data><data key="LabelDelegations">None</data><data key="Labels">None</data></node><node id="n201" labels=":GraphNode:SwitchFabric"><data key="labels">:GraphNode:SwitchFabric</data><data key="label">SwitchFabric</data><data key="x">410.09722222222223</data><data key="labels">:GraphNode:SwitchFabric</data><data key="y">195.0</data><data key="Name">NodeSwitchFabric1</data><data key="Model">None</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">SwitchFabric</data><data key="Type">SwitchFabric</data><data key="Capacities">{ "unit": 1 }</data><data key="CapacityDelegations">None</data><data key="NodeID">fd3bb283-3d0d-4d58-b0a1-a48e00d1040d</data><data key="id">n35</data><data key="Layer">L2</data><data key="LabelDelegations">None</data><data key="Labels">None</data></node><node id="n203" labels=":GraphNode:SwitchFabric"><data key="labels">:GraphNode:SwitchFabric</data><data key="x">530.0972222222222</data><data key="label">SwitchFabric</data><data key="y">268.98148148148147</data><data key="labels">:GraphNode:SwitchFabric</data><data key="Name">NICSwitchFabric2</data><data key="Model">None</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">SwitchFabric</data><data key="Type">SwitchFabric</data><data key="Capacities">{ "unit": 1 }</data><data key="CapacityDelegations">None</data><data key="NodeID">037bf341-1112-4cd3-a07c-2c6cb362307c</data><data key="id">n36</data><data key="Layer">L2</data><data key="LabelDelegations">None</data><data key="Labels">None</data></node><node id="n206" labels=":GraphNode:SwitchFabric"><data key="labels">:GraphNode:SwitchFabric</data><data key="label">SwitchFabric</data><data key="x">728.3981481481483</data><data key="labels">:GraphNode:SwitchFabric</data><data key="y">195.0</data><data key="Name">NodeSwitchFabric2</data><data key="Model">None</data><data key="GraphID">93758341-5053-47a5-b1fc-0b19c8d4f609</data><data key="Class">SwitchFabric</data><data key="Type">SwitchFabric</data><data key="Capacities">{ "unit": 1 }</data><data key="CapacityDelegations">None</data><data key="NodeID">3b093b50-a85f-488a-953c-8ad287c33eef</data><data key="id">n38</data><data key="Layer">L2</data><data key="LabelDelegations">None</data><data key="Labels">None</data></node><edge id="e172" source="n159" target="n200" label="has"><data key="label">has</data><data key="id">e2</data><data key="Class">None</data></edge><edge id="e173" source="n160" target="n159" label="has"><data key="label">has</data><data key="id">e11</data><data key="Class">None</data></edge><edge id="e175" source="n160" target="n158" label="has"><data key="label">has</data><data key="id">e20</data><data key="Class">None</data></edge><edge id="e177" source="n160" target="n201" label="has"><data key="label">has</data><data key="id">e22</data><data key="Class">None</data></edge><edge id="e178" source="n161" target="n167" label="connects"><data key="label">connects</data><data key="id">e25</data><data key="Class">None</data></edge><edge id="e179" source="n163" target="n170" label="connects"><data key="label">connects</data><data key="id">e28</data><data key="Class">None</data></edge><edge id="e180" source="n163" target="n168" label="connects"><data key="label">connects</data><data key="id">e29</data><data key="Class">None</data></edge><edge id="e181" source="n163" target="n171" label="connects"><data key="label">connects</data><data key="id">e33</data><data key="Class">None</data></edge><edge id="e182" source="n163" target="n192" label="connects"><data key="label">connects</data><data key="id">e34</data><data key="Class">None</data></edge><edge id="e183" source="n163" target="n193" label="connects"><data key="label">connects</data><data key="id">e41</data><data key="Class">None</data></edge><edge id="e186" source="n163" target="n198" label="connects"><data key="label">connects</data><data key="id">e45</data><data key="Class">None</data></edge><edge id="e189" source="n164" target="n166" label="connects"><data key="label">connects</data><data key="id">e48</data><data key="Class">None</data></edge><edge id="e190" source="n165" target="n162" label="connects"><data key="label">connects</data><data key="id">e50</data><data key="Class">None</data></edge><edge id="e191" source="n168" target="n162" label="connects"><data key="label">connects</data><data key="id">e51</data><data key="Class">None</data></edge><edge id="e192" source="n170" target="n166" label="connects"><data key="label">connects</data><data key="id">e53</data><data key="Class">None</data></edge><edge id="e193" source="n171" target="n167" label="connects"><data key="label">connects</data><data key="id">e54</data><data key="Class">None</data></edge><edge id="e195" source="n172" target="n163" label="has"><data key="label">has</data><data key="id">e57</data><data key="Class">None</data></edge><edge id="e198" source="n174" target="n177" label="has"><data key="label">has</data><data key="id">e65</data><data key="Class">None</data></edge><edge id="e200" source="n174" target="n206" label="has"><data key="label">has</data><data key="id">e67</data><data key="Class">None</data></edge><edge id="e201" source="n177" target="n203" label="has"><data key="label">has</data><data key="id">e68</data><data key="Class">None</data></edge><edge id="e204" source="n179" target="n187" label="connects"><data key="label">connects</data><data key="id">e71</data><data key="Class">None</data></edge><edge id="e205" source="n180" target="n188" label="connects"><data key="label">connects</data><data key="id">e73</data><data key="Class">None</data></edge><edge id="e210" source="n184" target="n191" label="connects"><data key="label">connects</data><data key="id">e77</data><data key="Class">None</data></edge><edge id="e211" source="n192" target="n187" label="connects"><data key="label">connects</data><data key="id">e78</data><data key="Class">None</data></edge><edge id="e212" source="n193" target="n188" label="connects"><data key="label">connects</data><data key="id">e79</data><data key="Class">None</data></edge><edge id="e218" source="n198" target="n191" label="connects"><data key="label">connects</data><data key="id">e85</data><data key="Class">None</data></edge><edge id="e220" source="n200" target="n164" label="connects"><data key="label">connects</data><data key="id">e87</data><data key="Class">None</data></edge><edge id="e221" source="n200" target="n161" label="connects"><data key="label">connects</data><data key="id">e89</data><data key="Class">None</data></edge><edge id="e222" source="n201" target="n165" label="connects"><data key="label">connects</data><data key="id">e90</data><data key="Class">None</data></edge><edge id="e224" source="n203" target="n179" label="connects"><data key="label">connects</data><data key="id">e91</data><data key="Class">None</data></edge><edge id="e226" source="n203" target="n180" label="connects"><data key="label">connects</data><data key="id">e94</data><data key="Class">None</data></edge><edge id="e230" source="n206" target="n184" label="connects"><data key="label">connects</data><data key="id">e100</data><data key="Class">None</data></edge></graph></graphml>
```
