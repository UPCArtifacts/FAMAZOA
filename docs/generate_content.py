import json
import sys
import subprocess
import argparse
from subprocess import PIPE
from datetime import datetime
from git import Repo
from git import GitCommandError
from git import InvalidGitRepositoryError
from pathlib import Path
import logging
import urllib.request

logging.basicConfig(level=logging.INFO, format='%(asctime)s | [%(levelname)s] : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def generate_config_file(number_of_apps, version_label, version_id):
    with open('templates/_config.yml', 'r') as config_file:
        config_content = config_file.readlines()

    with open('_config.yml', 'w') as new_config:
        new_config.write("".join(config_content))
        new_config.write('number_of_apps: {} \n'.format(number_of_apps))
        new_config.write('current_version: {} \n'.format(version_label))

def parse_json(input_file):
    result = []
    json_content = json.load(input_file)['apps']
    number_of_apps = len(json_content)

    generate_config_file(number_of_apps, version_label, version_id)

#    for i, app in enumerate(json_content):


parser = argparse.ArgumentParser()
parser.add_argument("--apps_list",
        type=argparse.FileType('r'),
        help="The json file containing the repositories to download",
        required=True)

parser.add_argument("--version_id",
        type=float,
        help="Version id",
        required=True)

parser.add_argument("--version_label",
        type=str,
        help="Version label",
        required=True)

parser.add_argument("--version_date",
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        help="Version's date of update (YYYY-MM-DD)",
        required=True)

parser.add_argument("--online_info_date",
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        help="Date of online information checking (YYYY-MM-DD)",
        required=True)

args = parser.parse_args()
input_file = args.apps_list
version_id = args.version_id
version_label = args.version_label
version_date = args.version_date
version_id = args.version_id
online_date = args.online_info_date

if input_file.name.endswith(".json"):
    parse_json(input_file)


