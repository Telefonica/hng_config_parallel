
# Usage

## Generate hng-config-generator

To generate container unit use the following

```
packer build scripter.json 
```

## Execution in the CI/CD pipeline

Generate HNG Config:

```
docker run -v /home/research/core-networkcloud-dockerfiles/hng-config-gen/app:/app -it dockerhub.tid.es/networkcloud/hng-config-gen:5.0.1-1 examples/hngv4.yml
```

A file named hngv4.txt with the following sort of output will be generated:

```
!!!!!!!!!!!!!!!!!!!!!!!!!!! HNG CONFIGURATION !!!!!!!!!!!!!!!!!!!!!!!!!!!
! 
!
system node primary
!
interface pOAM ip address 192.168.10.9 port eth0 netmask 255.255.255.0 broadcast 192.168.10.255
interface pRAN ip address 192.168.12.11 port eth2 netmask 255.255.255.0 broadcast 192.168.12.255
interface pCORE ip address 192.168.13.7 port eth3 netmask 255.255.255.0 broadcast 192.168.13.255
interface pSON ip address 192.168.12.15 port lo netmask 255.255.255.0 broadcast 192.168.12.255
!
virtual-network toparentip
interface fl-toparentip address 192.168.13.8 description "A test"
policy-routing route-table PRUEBA route address 0.0.0.0 gateway 192.168.13.1 port eth3
rule prioriy 201 table PRUEBA source 192.168.13.8
sctp endpoint sctp.endpoint bind-address 192.168.13.8 sctp-port 36412 sctp-profile default
gtpu endpoint gtpu.endpoint bind-address 192.168.13.8 gtpu-port 2152 gtpu-profile default
virtual-network tokidip
interface fl-tokidip address 192.168.12.8 description "A test"
policy-routing route-table tokidip route address 0.0.0.0 gateway 192.168.12.8 port eth2
rule prioriy 202 table tokidip source 192.168.12.8
sctp endpoint sctp.endpoint bind-address 192.168.12.8 sctp-port 36412 sctp-profile default
gtpu endpoint gtpu.endpoint bind-address 192.168.12.8 gtpu-port 2152 gtpu-profile default
!
lte mme Parent s1ap-layer sctp ipaddr 192.168.13.2 sctp port 36412
!
!
! gateway configuration
gateway  LAB congestion admin-state disabled call-control admin-state enabled
!
lte macro-zone band28Lte access s1ap-layer virtual-network tokidip intf tokidip-S1C
!
lte macro-zone band28Lte access gtpu-layer virtual-network tokidip intf tokidip-S1U
!
lte macro-zone band28Lte core gtpu-layer virtual-network toparentip intf toparentip-S1U
!
lte macro-zone band28Lte core s1ap-layer virtual-network toparentip intf toparentip-S1C mme Parent admin-state enabled
```
