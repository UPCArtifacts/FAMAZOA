from datetime import date
from datetime import timedelta
import subprocess

### Check these values before run #########################
crawler_dir="/Users/brunomateus/MyProjects/F-DroidCrawler/"
last_update = date(2018, 12, 12)
###########################################################

start_date = last_update + timedelta(days=1)
running_date = date.today()

new_json_apps_filename ="all_apps_from_{}_run_{}.json".format(start_date.strftime("%d_%m_%Y"),  running_date.strftime("%d_%m_%Y")) 

scrap_cmd_args = "scrapy crawl apps -a start_date={} -o {} -t json".format(start_date.strftime("%d-%m-%Y"), new_json_apps_filename)

print('scrapy crawl apps {}'.format(scrap_cmd_args.split()))

process = subprocess.run(scrap_cmd_args.split(), cwd=crawler_dir, universal_newlines=True, check=True)

if process.returncode != 0:
    exit()
else:
    print("Applications crawled with sucess.")
    process = subprocess.run('cp {}{} .'.format(crawler_dir, new_json_apps_filename), shell=True, universal_newlines=True, check=True)
    print("CHECK the output file => {}".format(new_json_apps_filename))
