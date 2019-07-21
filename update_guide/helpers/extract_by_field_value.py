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

       
def get_from_json(value, field, json_content, sensitive):
    for app in json_content:
        app_field = app.get(field, "").strip()

        if not sensitive :
            if app_field.strip().upper() == value.upper():
                return app
        elif(app_field == value):
            return app

    return None

def get_all_from_json(field, json_content):
    result = []
    total = len(json_content)
    for (i, app) in enumerate(json_content):

        n_values = i + 1
        workdone = n_values/total
        print("\rProgress: [{0:50s}] {1:.1f}% {2}/{3}".format('#' * int(workdone * 50), workdone*100, n_values, total), end='', flush=True)

        if(app.get(field, None)):
            result.append(app)

    return result


def parse_json(input_file,field, values=None, sensitive=True):
    result = []
    json_content = json.load(input_file)
    if 'apps' in json_content: 
        content = json_content.pop('apps')
    else:
        content = json_content
    if values:
        number_of_values = len(list(values))
        for (i, v) in enumerate(values):
            n_values = i + 1
            workdone = n_values/number_of_values
            print("\rProgress: [{0:50s}] {1:.1f}% {2}/{3}".format('#' * int(workdone * 50), workdone*100, n_values, number_of_values), end='', flush=True)

            item = get_from_json(v.strip(), field, content, sensitive)
            if(item):
                result.append(item)

        print("\nFrom {} values, {} apps  were found." .format(n_values, len(result)))
    else:
        result = get_all_from_json(field, content)

    return result



parser = argparse.ArgumentParser()
parser.add_argument("--apps_list",
        type=argparse.FileType('r'),
        help="The json file containing the repositories to extract language",
        required=True)

parser.add_argument("--field",
        type=str,
        help="JSON field to compare",
        required=True)

parser.add_argument("--values",
        type=argparse.FileType('r'),
        help="File containing a list of values to be searched",
        default=None )


parser.add_argument("--case_sensitive",
        action='store_false',
        help="Output file to store the result",
        default=True)

parser.add_argument("--output",
        type=argparse.FileType('w'),
        help="Output file to store the result",
        default=sys.stdout)

args = parser.parse_args()
input_file = args.apps_list
field = args.field
case_sensitive = args.case_sensitive

values = args.values.readlines() if args.values is not None else args.values


result = dict()

if input_file.name.endswith(".json"):
    result = parse_json(input_file, field, values, sensitive=case_sensitive)

print(json.dumps(result, indent=4, sort_keys=False), file=args.output)
