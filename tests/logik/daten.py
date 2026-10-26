"""Erfundene Beispieldaten der Box (keine echten Geräte, Adressen aus Dokumentationsbereichen)."""

HOSTLISTE = """<?xml version="1.0"?><List>
<Item><Index>1</Index><IPAddress>192.168.170.60</IPAddress><MACAddress>00:11:22:33:44:01</MACAddress><Active>1</Active>
 <HostName>homeassistant</HostName><InterfaceType>Ethernet</InterfaceType><X_AVM-DE_Port>1</X_AVM-DE_Port>
 <X_AVM-DE_Guest>0</X_AVM-DE_Guest><X_AVM-DE_VPN>0</X_AVM-DE_VPN><X_AVM-DE_WANAccess>granted</X_AVM-DE_WANAccess>
 <X_AVM-DE_Disallow>0</X_AVM-DE_Disallow><X_AVM-DE_FriendlyName>Pi</X_AVM-DE_FriendlyName></Item>
<Item><Index>2</Index><IPAddress>192.168.170.60</IPAddress><MACAddress>00:11:22:33:44:02</MACAddress><Active>1</Active>
 <HostName>fernseher</HostName><InterfaceType>802.11</InterfaceType><X_AVM-DE_WANAccess>granted</X_AVM-DE_WANAccess></Item>
<Item><Index>3</Index><IPAddress>192.168.1.23</IPAddress><MACAddress>02:11:22:33:44:03</MACAddress><Active>1</Active>
 <HostName>Tab</HostName><InterfaceType>802.11</InterfaceType></Item>
<Item><Index>4</Index><IPAddress>192.168.170.40</IPAddress><MACAddress>00:11:22:33:44:04</MACAddress><Active>1</Active>
 <HostName>kind</HostName><InterfaceType>802.11</InterfaceType><X_AVM-DE_WANAccess>denied</X_AVM-DE_WANAccess></Item>
<Item><Index>5</Index><IPAddress></IPAddress><MACAddress>02:11:22:33:44:05</MACAddress><Active>1</Active><HostName>Switch</HostName></Item>
</List>"""

GERAETELOG = """<?xml version="1.0"?><root>
<Event><id>23</id><group>2</group><date>19.09.26</date><time>10:05:00</time><msg>Internetverbindung wurde getrennt.</msg></Event>
<Event><id>751</id><group>4</group><date>19.09.26</date><time>10:01:00</time><msg>WLAN-Gerät | abgemeldet</msg></Event>
</root>"""

ZELLEN = (
    "<CellList><Cell><Index>0</Index><Connected>primary</Connected><CellType>lte</CellType><PLMN>23205</PLMN><Provider>3 AT</Provider><TAC>C0FC</TAC>"
    "<PhysicalId>443</PhysicalId><Distance>1350</Distance><Rssi>-69</Rssi><Rsrq>-11</Rsrq><RSRP>-100</RSRP><Cellid>abcde-0b</Cellid></Cell>"
    "<Cell><Index>8</Index><Connected>secondary</Connected><CellType>nr5g</CellType><Provider>3 AT</Provider><PhysicalId>121</PhysicalId>"
    "<Distance>0</Distance><Rssi>0</Rssi><Rsrq>-10</Rsrq><RSRP>-94</RSRP><Cellid/></Cell></CellList>"
)

WLANLISTE = """<?xml version="1.0" encoding="UTF-8"?><List><TotalAssociations>3</TotalAssociations>
<Item><AssociatedDeviceMACAddress>00:11:22:33:44:02</AssociatedDeviceMACAddress><X_AVM-DE_Speed>866</X_AVM-DE_Speed>
 <X_AVM-DE_SignalStrength>92</X_AVM-DE_SignalStrength><AssociatedDeviceChannel>44</AssociatedDeviceChannel><AssociatedDeviceGuest>0</AssociatedDeviceGuest></Item>
<Item><AssociatedDeviceMACAddress>02:11:22:33:44:03</AssociatedDeviceMACAddress><X_AVM-DE_Speed>6</X_AVM-DE_Speed>
 <X_AVM-DE_SignalStrength>18</X_AVM-DE_SignalStrength><AssociatedDeviceChannel>6</AssociatedDeviceChannel><AssociatedDeviceGuest>0</AssociatedDeviceGuest></Item>
<Item><AssociatedDeviceMACAddress>00:11:22:33:44:04</AssociatedDeviceMACAddress><X_AVM-DE_Speed>144</X_AVM-DE_Speed>
 <X_AVM-DE_SignalStrength>55</X_AVM-DE_SignalStrength><AssociatedDeviceChannel>6</AssociatedDeviceChannel><AssociatedDeviceGuest>0</AssociatedDeviceGuest></Item>
</List>"""

# Mesh-Liste der Box (X_AVM-DE_GetMeshListPath, gekürzt): Box, ein Repeater, ein Client (nicht im Mesh)
MESH = """{"schema_version": "4.6", "nodes": [
 {"device_name": "fritz.box", "device_model": "FRITZ!Box 6860 5G", "device_mac_address": "AA:00:00:00:00:01",
  "is_meshed": true, "mesh_role": "master", "node_interfaces": [{"mac_address": "AA:00:00:00:00:01"}]},
 {"device_name": "Repeater", "device_model": "FRITZ!Repeater 3000", "device_mac_address": "AA:00:00:00:00:02",
  "is_meshed": true, "mesh_role": "slave", "node_interfaces": [{"mac_address": "00:11:22:33:44:04"}]},
 {"device_name": "Handy", "device_mac_address": "AA:00:00:00:00:03", "is_meshed": false, "mesh_role": "unknown"}
]}"""
