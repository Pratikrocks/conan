# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/pombredanne/conan/
# The Conan software is licensed under the Apache License version 2.0.
# Data generated with Conan require an acknowledgment.
# Conan is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# spec

from __future__ import print_function, absolute_import
from posixpath import exists, join
from pprint import pprint

import csv
import json
import sys


def parse_manifest_json(input):
    layers_list = []
    input_json = join(input, 'manifest.json')
    with open(input_json) as manifest_json:    
        info = json.load(manifest_json)
    for data in info:
        config = data['Config']
        layers_id = data['Layers']
        # FIXME
        # The data['RepoTags'] is a list, and I've checked only the list always
        # contians 1 element. Hard-coded for now
        repo_tags = data['RepoTags'][0]
        layer_info = get_layer_id_command(input, config, layers_id)
        # The layer_info should not be empty.
        if layer_info:
            layer_list = update_info_to_dict(layer_info, repo_tags)
            layers_list.append(layer_list)
    return layers_list

def get_layer_id_command(input_path, config, layers_id):
    layer_command = []
    layer_info = []
    layer_id_with_command = {}
    config_json = join(input_path, config)
    if exists(config_json):
        with open(config_json) as manifest_json:    
            info = json.load(manifest_json)
            layer_command = info['history']
        # The size of the layer_ids list should be the same as the layer_command list
        if (len(layers_id) == len(layer_command)):
            layer_order = 0
            while layer_order < len(layers_id):
                layer_id_with_command = []
                # We only want to get the id and get rid of the layer.tar
                layer_id = layers_id[layer_order].partition('/layer.tar')[0]
                layer_id_with_command.append(layer_id)
                layer_id_with_command.append(layer_order)
                layer_id_with_command.append(layer_command[layer_order])
                layer_order = layer_order + 1
                layer_info.append(layer_id_with_command)
        else:
            print('The size of the layer_id does not match with the layer_command.')
            print('Please check.')
    else:
        print("The config files: %(config)r does not exist." % locals())
    return layer_info


def update_info_to_dict(layer_info, repo_tags):
    layer_dictionary_list = []
    for info in layer_info:
        layer_id = info[0]
        layer_order = info[1]
        layer_data = info[2]
        layer_data[u'layer_id'] = layer_id
        layer_data[u'layer_order'] = layer_order
        layer_data[u'repo_tags'] = repo_tags
        # Check if the dictionary list has the keys that we want
        try:
            if not layer_data['author']:
                pass
        except Exception as e:
            layer_data[u'author'] = ''
        layer_dictionary_list.append(layer_data)
    return layer_dictionary_list
    


def write_to_csv(layers_list, output_file):
    keys = layers_list[0][0].keys()
    with open(output_file, 'wb') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        for items in layers_list:
            dict_writer.writerows(items)

def main(argv):
    args = sys.argv[1:]
    input_path = args[0]
    output_file = args[1]
    layers_list = parse_manifest_json(input_path)
    write_to_csv(layers_list, output_file)


if __name__ == "__main__":
    main(sys.argv[1:])
