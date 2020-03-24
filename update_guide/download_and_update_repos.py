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
import requests
import time

logging.basicConfig(format='%(asctime)s | [%(levelname)s] : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

error_log = logging.FileHandler('error.log', delay=True)
error_log.setLevel(logging.ERROR)
logger.addHandler(error_log)
error_log.close()

headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15',
        'referer': 'https://try.kotlinlang.org/',
        'Accept-Language': 'pt-br',
        'Accept-Encoding': 'br, gzip, deflate'
}

def is_online(url):
    try:
        response  = requests.get(url, headers=headers)
    except requests.exceptions.RequestException:
        return False
    return response.status_code == 200

def clone_repo(repo_url, folder):
    repo_url = repo_url.replace("https://", "https://:@")
    repo = None
    try:
        logging.info("Cloning a new repo {}->{}".format(repo_url, folder))
        repo = Repo.clone_from(repo_url, folder)
        return repo
    except GitCommandError as exc:
        logging.warn("Skipped {}, an error ocurred {}".format(repo_url, exc))
        return None

def cloc_info(repo):
    repo_dir = Path(repo.git_dir).parent
    logging.debug('Running cloc {}'.format(repo_dir))
    process = subprocess.run("cloc --git . --json", cwd=repo_dir, universal_newlines=True, check=True, shell=True, stdout=PIPE, stderr=PIPE)
    if process.returncode != 0:
        logging.error(process.stderr)
        return None
    else:
        result = json.loads(process.stdout)
        total_nfiles = result.pop('header').get('n_files')  
        total = result.pop('SUM')
        languages = {}
        for l in result:
            lang_details = {}
            lang_details['proportion'] = (result.get(l).get('code')/total.get('code'))*100
            lang_details['files'] = result.get(l).get('nFiles')
            lang_details['sloc'] = result.get(l).get('code')
            languages[l] = lang_details
        return (total_nfiles ,languages)
 
def get_info(repo):
    logging.debug('Retriving information about the repository')
    commits = list(repo.iter_commits())
    n_commits = 0
    contrib = set()
    for c in commits:
        contrib.add(c.author)
        n_commits = n_commits + 1
    active = repo.active_branch
    # call cloc
    nfiles, languages = cloc_info(repo)
    first_commit = commits[-1].committed_date
    last_commit =  repo.head.commit.committed_date
    first_commit_dic = {
            'date': time.strftime("%d-%m-%Y", time.gmtime(first_commit)),
            'timestamp': first_commit,
            'hash': commits[-1].hexsha
            }

    last_commit_dic = {
            'date': time.strftime("%d-%m-%Y", time.gmtime(last_commit)),
            'timestamp': last_commit,
            'hash': repo.head.commit.hexsha
    }
    
    return {'commits': n_commits,
            'files': nfiles,
            'languages': languages,
            'contributors': len(contrib), 
            'active_branch': active.name,
            'active_period':  int((last_commit - first_commit)/86400),
            'initial_commit': first_commit_dic,
            'last_commit': last_commit_dic }
 

       
def parse_json(input_file, repos_dir):
    result = []
    json_content = json.load(input_file)['apps']
    n_errors = 0
    n_news = 0
    n_updated = 0
    off = 0
    off_in_disk = 0
    number_of_apps = len(json_content)

    for i, app in enumerate(json_content):

        package = app["package"]
        repo_url_str = app.get("source_repo").strip()
        destiny_folder = "{}/{}".format(repos_dir, package.replace(".", "-"))

        logging.info("{}/{} application".format(i + 1, number_of_apps))
        p = Path(destiny_folder)

        repo_on = is_online(repo_url_str)

        app['status'] = {
                'store_on' : is_online("https://play.google.com/store/apps/details?id={}".format(package)),
                'fdroid_on' : is_online("https://f-droid.org/en/packages/{}/".format(package)),
                'repo_on' : repo_on
                }

        if repo_on:
            if p.exists() and p.is_dir():
                logging.info("Repository of application {}[{}] already exist!".format(app['name'], package))
                try:
                     repo = Repo(str(p))
                     if repo_url_str.replace("https://", "https://:@") != repo.remote('origin').url:
                         logging.warn("Repository exist {}[{}] with a different remote {} -> {}".format(app['name'], package, repo_url_str, repo.remote('origin').url)) 
                         repo.close()
                         logging.debug("Moving repo to avoid conflic")
                         process = subprocess.run("mv {} conflict/".format(str(p)), universal_newlines=True, check=True, shell=True, stdout=PIPE, stderr=PIPE)
                         if process.returncode != 0:
                             logging.error(process.stderr)
                         repo = clone_repo(repo_url_str, str(p))
                         n_news = n_news + 1
                     else:
                        n_updated = n_updated + 1
                        active_branch = repo.active_branch
                        origin = repo.remote('origin')
                        info = origin.pull(active_branch)
                        logging.info("Updating repo from {} {}".format(origin.name, active_branch))
                        for i in info:
                            logging.debug("Last commit found {}".format(i.commit))

                except InvalidGitRepositoryError as e:
                    logging.erro("Existent repository {}[{}], is not a git repo".format(app['name'], package))
                
            else:
                repo = clone_repo(repo_url_str, str(p))
                n_news = n_news + 1
        else:
            if p.exists() and p.is_dir():
                logging.info("Repository is offline, but there is old version in disk {}[{}]!".format(app['name'], package))
                try:
                     repo = Repo(str(p))
                     off_in_disk = off_in_disk + 1
                except InvalidGitRepositoryError as e:
                    logging.erro("Existent repository {}[{}], is not a git repo".format(app['name'], package))
                    off = off + 1
            else:
                logging.error("Repo {},{}-[{}] offline and no version found in disk".format(app['name'], package, repo_url_str))
                off = off + 1
                result.append(app)
                continue

        info = get_info(repo)
        app = {**app, **info}
        repo.close()
        result.append(app)

    logging.info("From {} apps, {} were cloned, {} were updated, {} offline in disk, {} offline and {} failed." .format(number_of_apps, n_news, n_updated, off_in_disk, off, n_errors))
    return result


parser = argparse.ArgumentParser()
parser.add_argument("--apps_list",
        type=argparse.FileType('r'),
        help="The json file containing the repositories to download",
        required=True)

parser.add_argument("--repos_dir",
        type=str,
        help="Folder to save the repos",
        required=True)

parser.add_argument("--output",
        type=argparse.FileType('w'),
        help="JSON file containing the apps with updated info",
        required=True)

args = parser.parse_args()
input_file = args.apps_list
repos_dir = args.repos_dir

p = Path(repos_dir)
if not p.exists() or not p.is_dir():
    exit("Repos_dir does not exist")


if input_file.name.endswith(".json"):
    result = parse_json(input_file, repos_dir)


print(json.dumps({ "apps": result}, indent=4, sort_keys=False), file=args.output)
