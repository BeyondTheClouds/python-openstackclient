#   Copyright 2016 Huawei, Inc. All rights reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

"""Compute v2 Server Group action implementations"""

from openstackclient.common import command
from openstackclient.common import exceptions
from openstackclient.common import utils


_formatters = {
    'policies': utils.format_list,
    'members': utils.format_list,
}


def _get_columns(info):
    columns = list(info.keys())
    if 'metadata' in columns:
        # NOTE(RuiChen): The metadata of server group is always empty since API
        #                compatible, so hide it in order to avoid confusion.
        columns.remove('metadata')
    return tuple(sorted(columns))


class CreateServerGroup(command.ShowOne):
    """Create a new server group."""

    def get_parser(self, prog_name):
        parser = super(CreateServerGroup, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help='New server group name',
        )
        parser.add_argument(
            '--policy',
            metavar='<policy>',
            action='append',
            required=True,
            help='Add a policy to <name> '
                 '(repeat option to add multiple policies)',
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        info = {}
        server_group = compute_client.server_groups.create(
            name=parsed_args.name,
            policies=parsed_args.policy)
        info.update(server_group._info)

        columns = _get_columns(info)
        data = utils.get_dict_properties(info, columns,
                                         formatters=_formatters)
        return columns, data


class DeleteServerGroup(command.Command):
    """Delete an existing server group."""

    def get_parser(self, prog_name):
        parser = super(DeleteServerGroup, self).get_parser(prog_name)
        parser.add_argument(
            'server_group',
            metavar='<server-group>',
            nargs='+',
            help='server group(s) to delete (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        result = 0
        for group in parsed_args.server_group:
            try:
                group_obj = utils.find_resource(compute_client.server_groups,
                                                group)
                compute_client.server_groups.delete(group_obj.id)
            # Catch all exceptions in order to avoid to block the next deleting
            except Exception as e:
                result += 1
                self.app.log.error(e)

        if result > 0:
            total = len(parsed_args.server_group)
            msg = "%s of %s server groups failed to delete." % (result, total)
            raise exceptions.CommandError(msg)