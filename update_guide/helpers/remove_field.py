import json
import sys
import subprocess
import argparse
from subprocess import PIPE
from datetime import datetime
from github import Github
from github.GithubException import RateLimitExceededException
from github.GithubException import UnknownObjectException
from github.GithubException import GithubException
from urllib.parse import urlparse
from git import Repo
from git import GitCommandError
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | [%(levelname)s] : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

       
def remove_all_fields_from_json(fields, json_content):
    result = []
    total = len(json_content)
    for (i, app) in enumerate(json_content):

        n_values = i + 1
        workdone = n_values/total
        print("\rProgress: [{0:50s}] {1:.1f}% {2}/{3}".format('#' * int(workdone * 50), workdone*100, n_values, total), end='', flush=True)

        for field in fields:
            app.pop(field, None)
        result.append(app)

    return result


def parse_json(input_file,fields):
    result = []
    json_content = json.load(input_file)
    if 'apps' in json_content: 
        content = json_content.pop('apps')
    else:
        content = json_content

    result = remove_all_fields_from_json(fields, content)

    return result



parser = argparse.ArgumentParser()
parser.add_argument("--apps_list",
        type=argparse.FileType('r'),
        help="The json file containing a list of apps",
        required=True)

parser.add_argument("-f", "--field",
        action="append",
        type=str,
        help="Field to remove. It's possible to use this multiple times",
        required=True)

parser.add_argument("--output",
        type=argparse.FileType('w'),
        help="Output file to store the result",
        default=sys.stdout)

args = parser.parse_args()
input_file = args.apps_list
fields = args.field

result = dict()

if input_file.name.endswith(".json"):
    result = parse_json(input_file, fields)

print(json.dumps(result, indent=4, sort_keys=False), file=args.output)
