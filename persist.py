import csv
import json
import os
from unidecode import unidecode
import logging
import datetime
import shutil

def persist(data, fieldnames, root, project_name=None, write_header=True, output_directory=os.getenv('OUTPUT_DIRECTORY','./'),):
    # Set up root data dir
    git_dir = output_directory + root + '/' + project_name + '/'
    root_filename = git_dir + '/automated/' + root + '/'

    # Clone data repository for updates - continue if already exists
    from sh import git
    try:
        shutil.rmtree(git_dir)
    except:
        pass
    
    if os.getenv('REMOTE'):
        git('config', '--global', 'user.email', os.getenv('MACHINE_AUTH').split(':')[0])
        git('config', '--global', 'user.name', os.getenv('MACHINE_AUTH').split(':')[0])
    git.clone('https://'+os.getenv('MACHINE_AUTH')+'@github.com/coffenbacher/%s.git' % project_name, git_dir)
    
    # Create our root if required
    if not os.path.exists(root_filename):
        os.makedirs(root_filename)
    
    # Set up logging
    logging.basicConfig(level='WARNING',
                    #format='%(asctime)s %(levelname)-8s %(message)s',
                    #datefmt='%a, %d %b %Y %H:%M:%S',
                    filename= root_filename + root + '.log',
                    filemode='w')
    
    # Write everything to csv
    with open(root_filename + root + '.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        if write_header:
            writer.writeheader()
        for d in data:
            asci = dict([(unidecode(k), unidecode(unicode(v))) for k, v in d.items()])
            writer.writerow(asci)


    # Write everything to json
    with open(root_filename + root + '.json', 'w') as jsonfile:
        relevant = [{f: d.get(f, None) for f in fieldnames} for d in data]
        jsonfile.write(json.dumps(relevant, sort_keys=True, indent=4, separators=(',', ': ')))
    
    with open(root_filename + root + '_meta.json', 'w') as metafile:
        d = {
                'created': datetime.datetime.now().strftime('%x %X'),
                'rows': len(data),
                'headers': ','.join(fieldnames),
            }
        metafile.write(json.dumps(d))
        
    git = git.bake(**{'git-dir': root + '/%s/.git/' % project_name, 'work-tree': root + '/%s' % project_name})
    git.commit(m='Auto updating %s data' % root, a=True)
    git.push('origin', 'master')
    
    
if __name__ == '__main__':
    generate_csv()