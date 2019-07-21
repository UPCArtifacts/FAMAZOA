import json
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | [%(levelname)s] : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

parser = argparse.ArgumentParser()
parser.add_argument("--dataset_1",
        type=argparse.FileType('r'),
        help="The json file containg applications",
        required=True)

parser.add_argument("--dataset_2",
        type=argparse.FileType('r'),
        help="The json file containg applications",
        required=True)


parser.add_argument("--output",
        type=argparse.FileType('w'),
        help="Output file to store the result",
        required=True)

args = parser.parse_args()

dataset1 = json.load(args.dataset_1)
if 'apps' in dataset1:
    dataset1 = dataset1['apps']

dataset2 = json.load(args.dataset_2)
if 'apps' in dataset2:
    dataset2 = dataset2['apps']



bigger = dataset1
smaller = dataset2

if len(dataset1) < len(dataset2):
    smaller = dataset1
    bigger = dataset2

combined = bigger + smaller
logging.info("dataset1:{}, dataset2: {}, combined: {}".format(len(smaller), len(bigger), len(combined)))

total = len(combined)
intersection = []
logging.info("Finding commons")
for i, app in enumerate(bigger):

    updated_app = None
    for app2 in smaller:
        
        if app['package'] == app2['package']:
            merged = {**app, **app2}
            logging.info("{} duplicated".format(app['package']))
            intersection.append(merged)
            break

logging.info("{} apps of intersection".format(len(intersection)))

d = 0
to_remove = []

merged_pkgs = [app['package'] for app in intersection]
result = [app for app in combined if app['package'] not in  merged_pkgs]

combined = result + intersection

logging.info("Final size {}".format(len(combined)))
print(json.dumps({ "apps": combined }, indent=4, sort_keys=False), file=args.output)



