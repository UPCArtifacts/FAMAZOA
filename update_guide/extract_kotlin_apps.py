import json
import sys
import os.path
from datetime import datetime
from github import Github
from github.GithubException import RateLimitExceededException
from github.GithubException import UnknownObjectException
from urllib.parse import urlparse

def get_language_from_github(repo_url, g):
    repo_name = repo_url.path[1:]
    try:
        repo = g.get_repo(repo_name)
        languages= repo.get_languages()
        total_of_bytes = sum(languages.values())
        for l in languages:
            languages[l] = (languages[l]/total_of_bytes)*100
        if languages.get('Kotlin', None):
            releases = repo.get_releases().totalCount
            commits = repo.get_commits()
            return {'commits': commits.totalCount, 'releases': releases.totalCount, 'languages': languages}
        else:
            return {'languages': languages}
    except UnknownObjectException as e:
        print("Impossible to recover language stats from: [%s](%s) - %s" % (repo_name, repo_url.geturl(), e), file=sys.stderr)
        raise e
    except Exception as e:
        print(": [%s](%s) - %s" % (repo_name, repo_url.geturl(), e), file=sys.stderr)
        raise e

def get_language_with_cloc(repo_url):
    return None
        
def parse_json(input_file, g):
    result = []
    json_content = json.load(open(input_file))
    n_apps = 0
    n_errors = 0
    has_kotlin = 0
    not_in_gh = 0
    without_repo = 0
    for app in json_content:
        n_apps += 1

        if app.get("source_repo", None):
            repo_url_str = app.get("source_repo").strip()
            repo_url = urlparse(repo_url_str)

            package = app["last_download_url"].split('_')[0][len("https://f-droid.org/repo/"):]

            app_with_lang = None
            if repo_url.netloc == "github.com":
                try:
                    app_with_lang = {**get_language_from_github(repo_url, g), **app}
                except:
                    app_with_lang = get_language_with_cloc(repo_url_str)
            else:
                print("This app {} is not hosted on github -> {}".format(app['name'], repo_url_str), file=sys.stderr)
                app_with_lang = get_language_with_cloc(repo_url_str)
                not_in_gh = not_in_gh + 1
        else:
            print("This app {} does not have a source code repo url".format(app['name']), file=sys.stderr)
            without_repo = without_repo + 1

        if app_with_lang and ("Kotlin" in app_with_lang['languages']):
            has_kotlin = has_kotlin + 1
            app_with_lang["package"] = package
#            print(app_with_lang)
            result.append(app_with_lang)
        else:
            n_errors +=1
    print("From {} apps, {} are not in github, {} does provide repo url, {} failed and {} have Kotlin" .format(n_apps, not_in_gh, without_repo, n_errors, has_kotlin), file=sys.stderr)

    return result

input_file = sys.argv[1]

if len(input_file) == 0:
   exit(0) 

result = dict()

g = Github("brunomateus", "gitdiebetz170386")

if input_file.endswith(".json"):
    result["apps"] = parse_json(input_file, g)

print(json.dumps(result, indent=4, sort_keys=False))
