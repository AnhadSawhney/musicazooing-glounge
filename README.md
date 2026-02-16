NOTES ON NETWORKING:
We got ip banned by youtube at one point so we installed a second network card in the computer. 
Now there are two interfaces:

eno1 (on motherboard): receives a static ip from the MIT router. The website, ssh, all default traffic go through here.
enp2s0 (on pcie network card): received a dynamic ip from the MIT router. yt-dlp download traffic should only go through here so that youtube sees a constantly changing ip address that cannot get banned. 

In order to get this to work, we need the routing to change based on the source addresss
Normal routing rules work based on the destination address.

How do we change routing based on the source address?
-> Through an ip rule. 

Within ip rule you can create a rule that says if you re from this subnet, then you should use a different routing table than normal

we're putting the stuff for the dynamic interface into a new routing table. 

Lots of settings within networkmanager have been fiddled with to get this to work. 

Networkmanager is now the correct tool to use for network configuration. Connman is disabled and should not be used. 
The normal networking.service has been disabled by moving the configuration files for it in a new directory it is not pointed to. 
Everything should now be done through networkmanager. 

The default route is via the static interface

The routing rule ensures that ytdlp traffic goes through the dynamic interface

## Make the routing rules look like this: 

### IP RULE:
```
musicazoo@musicazoo:/etc/wireplumber/main.lua.d$ ip rule
0:      from all lookup local
16384:  from 10.238.0.0/21 lookup outr.enp2s0 proto static
32766:  from all lookup main
32767:  from all lookup default
```

### IP ROUTE:
```
musicazoo@musicazoo:/etc/wireplumber/main.lua.d$ ip route
default via 18.18.238.1 dev eno1 proto dhcp src 18.18.238.19 metric 100
18.18.238.0/24 dev eno1 proto kernel scope link src 18.18.238.19 metric 100
```

### ip route show table outr.enp2s0
```
musicazoo@musicazoo:/etc/wireplumber/main.lua.d$ ip route show table outr.enp2s0
default via 10.238.0.1 dev enp2s0 proto dhcp src 10.238.7.166 metric 101
10.238.0.0/21 dev enp2s0 proto kernel scope link src 10.238.7.166 metric 101
```

### nmcli con show
```
musicazoo@musicazoo:/etc/wireplumber/main.lua.d$ nmcli con show
NAME                     UUID                                  TYPE      DEVICE
Static IP (Motherboard)  fe94b809-04df-3dc7-9c88-9f52fb23a2fd  ethernet  eno1
Dynamic IP (card)        a3bb1835-0dd6-3d36-aee0-b7843dfc8569  ethernet  enp2s0
lo                       8b00b3ea-2ab9-4133-8775-72f76f795265  loopback  lo
```

On the static one, the mac address needs to be set properly. The "cloned" mac address is the one registered with MITnet to provide us a static ip and public hostname. 
the dynamic interface uses routing table 1. 

If you change things in ip route / ip addr / ip rule they will get overwritten when networkmanager restarts. So make sure to configure networkmanager properly to end up giving you the correct route/table/addr etc. 
Needed to install ffmpeg 
