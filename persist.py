import csv
import json
import os
from unidecode import unidecode
import logging
import datetime
import shutil

def persist(data, root, fieldnames=[], file_name=None, project_name=None, 
                write_header=True, write_meta=True, write_json=True, 
                write_csv=True, auto_add_file=False,
                output_directory=os.getenv('OUTPUT_DIRECTORY','./'),):
    """
    data should have schema:
    {
        'data': [],
        'name': 'e.g. coach_tenures',
        'fieldnames': [], //names for each field in order
    }
    """
    
    # Use root if file_name not set
    if not file_name:
        file_name = root
        
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
    if write_csv:
        with open(root_filename + file_name + '.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            if write_header:
                writer.writeheader()
            for d in data:
                asci = dict([(unidecode(k), unidecode(unicode(v))) for k, v in d.items()])
                writer.writerow(asci)


    # Write everything to json
    if write_json:
        with open(root_filename + file_name + '.json', 'w') as jsonfile:
            if isinstance(data, list) and fieldnames:
                relevant = [{f: d.get(f, None) for f in fieldnames} for d in data]
            else:
                relevant = data
            jsonfile.write(json.dumps(relevant, sort_keys=True, indent=4, separators=(',', ': ')))
    
    
    if write_meta:    
        with open(root_filename + file_name + '_meta.json', 'w') as metafile:
            d = {
                    'created': datetime.datetime.now().strftime('%x %X'),
                    'rows': len(data),
                    'headers': ','.join(fieldnames),
                }
            metafile.write(json.dumps(d))
        
    git = git.bake(**{'git-dir': root + '/%s/.git/' % project_name, 'work-tree': root + '/%s' % project_name})
    git.add('-A')
    git.commit(m='Auto updating %s data - file %s' % (root, file_name), a=True)
    git.push('origin', 'master')