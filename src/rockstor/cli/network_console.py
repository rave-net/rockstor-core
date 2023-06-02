"""
Copyright (c) 2012-2020 RockStor, Inc. <http://rockstor.com>
This file is part of RockStor.

RockStor is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

RockStor is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""


from base_console import BaseConsole
from rest_util import api_error, api_call
from subprocess import check_output, CalledProcessError


class NetworkConsole(BaseConsole):
    def __init__(self, prompt):
        BaseConsole.__init__(self)
        self.prompt = prompt + " Network>"
        self.baseurl = "%s/network" % BaseConsole.url

    @api_error
    def do_scan(self, args):
        """
        scan the system for any new network interfaces

        scan
        """
        network_info = api_call(self.baseurl, calltype="post")
        print(network_info)

    @api_error
    def do_list(self, args):
        """
        list all network interfaces known in the system
        """
        return self.do_scan(args)

    @api_error
    def do_config(self, args):
        """configure a network interface. dhcp and static ipv4 configurations are
        supported. Note that there is a risk of losing connectivity to the
        system. So this is best done via console connection.

        to configure using dhcp:
        config <interface> -d

        to configure static ip: config <interface> -s <ip_addr> <netmask>
        <gateway> <dns_servers> <domain>

        """
        fields = args.split()
        if len(fields) < 2:
            return self.do_help(args)
        url = "%s/%s" % (self.baseurl, fields[0])
        if fields[1] == "-d":
            print(api_call(url, data={"boot_protocol": "dhcp",}, calltype="put"))
        elif fields[1] == "-s":
            if len(fields) < 7:
                return self.do_help(args[:2])
            input_data = {
                "boot_protocol": "static",
                "ipaddr": fields[2],
                "netmask": fields[3],
                "gateway": fields[4],
                "dns_servers": fields[5],
                "domain": fields[6],
                "itype": "management",
            }
            print(api_call(url, data=input_data, calltype="put"))
        else:
            return self.do_help(args)
    @api_error
    def do_vlan_create(self, args):
        """
        Creates a new VLAN.
        vlan_create <vlan-name> <base-interface> <vlan-id>
        """
        fields = args.split()
        if len(fields) != 3:
            return self.do_help('vlan_create')

        vlan_name = fields[0]
        base_interface = fields[1]
        vlan_id = fields[2]

        cmd = ['nmcli', 'con', 'add', 'type', 'vlan', 'con-name', vlan_name, 'dev', base_interface, 'id', vlan_id]
        
        try:
            output = check_output(cmd)
            print('VLAN created successfully')
        except CalledProcessError as e:
            print(f'Failed to create VLAN: {e}')

    @api_error
    def do_vlan_delete(self, args):
        """
        Deletes an existing VLAN.
        vlan_delete <vlan-name>
        """        
        fields = args.split()
        if len(fields) != 1:
            return self.do_help('vlan_delete')

        vlan_name = fields[0]

        cmd = ['nmcli', 'con', 'delete', vlan_name]

        try:
            output = check_output(cmd)
            print('VLAN deleted successfully')
        except CalledProcessError as e:
            print(f'Failed to delete VLAN: {e}')

    @api_error
    def do_vlan_config(self, args):
        """
        Configures the IP address, netmask, and gateway for a VLAN.
        vlan_config <vlan-name> <ip-address>/<netmask> <gateway>
        """
        fields = args.split()
        if len(fields) != 3:
            return self.do_help('vlan_config')

        vlan_name = fields[0]
        ip_netmask = fields[1]
        gateway = fields[2]

        cmd = ['nmcli', 'con', 'mod', vlan_name, 'ipv4.addresses', ip_netmask, 'ipv4.gateway', gateway, 'ipv4.method', 'manual']

        try:
            output = check_output(cmd)
            print('VLAN configured successfully')
        except CalledProcessError as e:
            print(f'Failed to configure VLAN: {e}')

        cmd = ['nmcli', 'con', 'up', vlan_name]

        try:
            output = check_output(cmd)
            print('VLAN activated successfully')   
        
