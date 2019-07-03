import urllib.request
import sys
import yaml
import json

def check_arguments():
    number_of_args = len(sys.argv)
    output_options = ['txt', 'csv', 'yaml', 'json']
    output_type = 'txt'

    if(number_of_args < 2):
        print("The firt argument should be the path of a file contaning the links")
        exit()
    elif(number_of_args >= 3 and sys.argv[2] == '-t'):
        output_type = sys.argv[3]
        if(output_type not in output_options):
            print("Type invalid. The valid types are: {}".format(output_options))
            exit()

    return (sys.argv[1], output_type)



def output_list_to_dict(output):
    data = dict(apps = [])
    for (link, status) in output:
        data['apps'].append({
            'repo' : link,
            'status':status
        })
    return data


def print_output(output, formatt='txt', filename="result"):
    with open("{}.{}".format(filename, formatt),  'w') as out:
        if(formatt == 'txt'):
            for (link, status) in output:
                print("{} {}".format(link, status), file=out)
        elif(formatt == 'csv'):
            print("link,status", file=out)
            for (link, status) in output:
                print("{},{}".format(link, status), file=out)
        elif(formatt == 'json'):
            data = output_list_to_dict(output)
            print(json.dumps(data, indent=2), file=out)
        elif(formatt == 'yaml'):
            data = output_list_to_dict(output)
            print(yaml.dump(data, explicit_start=False, default_flow_style=False), file=out)


list_of_links, output_type = check_arguments()

output = []
num_lines = sum(1 for line in open(list_of_links))

with open(list_of_links) as f:
    for i, line in enumerate(f):
        j = (i + 1)/num_lines
        sys.stdout.write('\r')
        sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100*j))
        sys.stdout.flush()

        link = line.strip()
        http_status  = urllib.request.urlopen(link).getcode()
        output.append((link, http_status))

print_output(output, output_type)
