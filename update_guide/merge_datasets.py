import json
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | [%(levelname)s] : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

parser = argparse.ArgumentParser()
parser.add_argument("--dataset1",
        type=argparse.FileType('r'),
        help="The json file containg applications",
        required=True)

parser.add_argument("--dataset2",
        type=argparse.FileType('r'),
        help="The json file containg applications",
        required=True)


parser.add_argument("--output",
        type=argparse.FileType('w'),
        help="Output file to store the result",
        required=True)

args = parser.parse_args()

dataset1 = json.load(args.dataset1)
if 'apps' in dataset1:
    dataset1 = dataset1['apps']

dataset2 = json.load(args.dataset2)
if 'apps' in dataset2:
    dataset2 = dataset2['apps']



combined = dataset1 + dataset2
logging.info("dataset1:{}, dataset2: {}, combined: {}".format(len(dataset1), len(dataset2), len(combined)))

total = len(combined)
intersection = []
logging.info("Finding commons")
for i, app in enumerate(dataset1):

    updated_app = None
    for app2 in dataset2:
        
        if app['package'] == app2['package']:
            merged = {**app, **app2}
            logging.debug("{} duplicated".format(app['package']))
            intersection.append(merged)
            if app['source_repo'] != app2['source_repo']:
                logging.error("Same package [{}] different repo ({}) - ({})".format(app['package'], app['source_repo'], app2['source_repo'])) 
            break

logging.info("{} apps of intersection".format(len(intersection)))

d = 0
to_remove = []

merged_pkgs = [app['package'] for app in intersection]
result = [app for app in combined if app['package'] not in merged_pkgs]

combined = result + intersection

pkgs = {}

for app in combined:
    pkg = app['package']
    if 'source_repo' not in app:
        logging.error(app)
    pkgs.setdefault(pkg, []).append(app['source_repo'])
    if len(set(pkgs.get(pkg, list()))) > 1:
         logging.error("Same package [{}] different repo {}".format(pkg, pkgs.get(pkg))) 


logging.info("Final size {}".format(len(combined)))
print(json.dumps({ "apps": combined }, indent=4, sort_keys=False), file=args.output)



