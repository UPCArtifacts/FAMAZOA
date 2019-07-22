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

logging.basicConfig(level=logging.ERROR, format='%(asctime)s | [%(levelname)s] : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

       
def parse_json(input_file, g):
    result = []
    json_content = json.load(input_file)
    n_apps = 0
    n_errors = 0
    has_kotlin = 0
    not_in_gh = 0
    without_repo = 0
    number_of_apps = len(json_content)
    for app in json_content:
        n_apps += 1

        workdone = n_apps/number_of_apps
        print("\rProgress: [{0:50s}] {1:.1f}% {2}/{3}".format('#' * int(workdone * 50), workdone*100, n_apps, number_of_apps), end='', flush=True)


        if(app.get('package')):
            package = app["package"]
        else:
            app['package'] = app["last_download_url"].split('_')[0][len("https://f-droid.org/repo/"):]

        result.append(app)

    print("\nFrom {} apps, {} are not in github, {} does provide repo url, {} failed and {} have Kotlin" .format(n_apps, not_in_gh, without_repo, n_errors, has_kotlin))
    logging.info("From {} apps, {} are not in github, {} does provide repo url, {} failed and {} have Kotlin" .format(n_apps, not_in_gh, without_repo, n_errors, has_kotlin))


    return result


parser = argparse.ArgumentParser()
parser.add_argument("--apps_list",
        type=argparse.FileType('r'),
        help="The json file containing the repositories to extract language",
        required=True)

parser.add_argument("--output",
        type=argparse.FileType('w'),
        help="Output file to store the result",
        required=True)

args = parser.parse_args()
input_file = args.apps_list

result = dict()

g = Github(login_or_token="brunomateus", password="gitdiebetz170386")

try:
    g.get_user().login
except GithubException as e:
    logging.error("Requires authentication to continue")
    exit()

if input_file.name.endswith(".json"):
    result = parse_json(input_file, g)

print(json.dumps(result, indent=4, sort_keys=False), file=args.output)
