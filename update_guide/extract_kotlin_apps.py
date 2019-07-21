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

def get_language_from_github(repo_url, g):
    repo_name = repo_url.path[1:]
    try:
        repo = g.get_repo(repo_name)
        languages= repo.get_languages()
        total_of_bytes = sum(languages.values())
        for l in languages:
            languages[l] = (languages[l]/total_of_bytes)*100
        if languages.get('Kotlin', None):
            try:
                releases = repo.get_releases()
                commits = repo.get_commits()
                return {'commits': commits.totalCount, 'releases': releases.totalCount, 'languages': languages}
            except:
                logging.warning("Impossible to get commits or releases from [{}]({}) - {}".format(repo_name, repo_url.geturl(), e))
                return {'languages': languages}
        else:
            return {'languages': languages}
    except UnknownObjectException as e:
        logging.warning("Impossible to recover language stats from: [{}]({}) - {}".format(repo_name, repo_url.geturl(), e))
        raise e
    except Exception as e:
        raise e

def get_language_with_cloc(repo_url):
    repo_url = repo_url.replace("https://", "https://:@")
    repo = None
    try:
        logging.info("Cloning repo {}".format(repo_url))
        repo = Repo.clone_from(repo_url, "tmp")
    except GitCommandError as exc:
        logging.warning("Skipped {}, an error ocurred {}".format(repo_url, exc))
        return None

    n_commits = len(list(repo.iter_commits()))
    # call cloc
    process = subprocess.run("cloc --git . --json", cwd="tmp", universal_newlines=True, check=True, shell=True, stdout=PIPE, stderr=PIPE)
    if process.returncode != 0:
        logging.error(process.stderr)
        return None
    else:
        result = json.loads(process.stdout)
        result.pop('header') 
        total = result.pop('SUM')
        languages = {}
        for l in result:
            languages[l] = (result.get(l).get('code')/total.get('code'))*100

    repo.close()
    logging.info("Removing temporary repo")
    process = subprocess.run("rm -Rf tmp", universal_newlines=True, check=True, shell=True)
    return {'commits': n_commits, 'languages': languages} 
        
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

        if app.get("source_repo", None):
            repo_url_str = app.get("source_repo").strip()
            repo_url = urlparse(repo_url_str)

            package = app["package"]

            app_lang = None
            if repo_url.netloc == "github.com":
                try:
                    app_lang = get_language_from_github(repo_url, g)
                except:
                    app_lang = get_language_with_cloc(repo_url_str)
            else:
                logging.info("This app {} is not hosted on github -> {}".format(app['name'], repo_url_str))
                app_lang = get_language_with_cloc(repo_url_str)
                not_in_gh = not_in_gh + 1
        else:
            logging.info("This app {} does not have a source code repo url".format(app['name']))
            without_repo = without_repo + 1

        if app_lang:
            if ("Kotlin" in app_lang['languages']):
                has_kotlin = has_kotlin + 1
                app_with_lang = {**app_lang, **app}
                app_with_lang["package"] = package
                result.append(app_with_lang)
        else:
            n_errors +=1

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

g = Github(login_or_token="", password="")

try:
    g.get_user().login
except GithubException as e:
    logging.error("Requires authentication to continue")
    exit()

if input_file.name.endswith(".json"):
    result["apps"] = parse_json(input_file, g)

print(json.dumps(result, indent=4, sort_keys=False), file=args.output)
