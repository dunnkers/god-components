import os
from time import time
import pandas as pd
import subprocess

# Settings
KEY = os.environ.get('DESIGNITE_ENTERPRISE')
RUNTIME_JAR = 'designite/DesigniteJava_Enterprise.jar'
TIKA_REPO = '../tika'
OUTPUT_FOLDER = 'designite/reports'
# Vars
jar = 'java -jar {}'.format(RUNTIME_JAR)

# We require a license key
if (not KEY): exit('No Designite Enterprise key! See README to configure.')
# Register license if not registered yet
if (not os.path.exists('designite/.config')):
    os.system('{} -r {}'.format(jar, KEY))

# Run Designite on the currently checked out tag
def designite(output_folder):
    # Run Designite
    start = time()
    os.system('{} -i {} -o {}'.format(jar, TIKA_REPO, output_folder))
    print('Designite ran for {:.2f} seconds'.format(time() - start))

    # Filter results for God Components
    archsmells = pd.read_csv('{}/ArchitectureSmells.csv'.format(
        output_folder))
    godcomps = archsmells[archsmells['Architecture Smell'] == 'God Component'].copy()
    os.system('rm -rf {}'.format(output_folder)) # Remove report
    return godcomps

# Grab tags
tags = subprocess.check_output(['git', 'tag', '-l'],
    cwd=TIKA_REPO, encoding='utf-8').splitlines()
for tag in tags:
    targetfile = '{}/{}.csv'.format(OUTPUT_FOLDER, tag)
    if (os.path.exists(targetfile)):
        print('Skipping tag', tag)
        continue
    print('Running Designite for tag', tag)
    os.system('git checkout ' + tag)
    godcomps = designite('{}/{}'.format(OUTPUT_FOLDER, tag))
    godcomps['Tag'] = tag
    godcomps.to_csv(targetfile, index=False)

# Combine all reports into 1 .csv file
paths = map(lambda f: os.path.join(OUTPUT_FOLDER, f), os.listdir(OUTPUT_FOLDER))
all_reports = pd.concat(map(lambda f: pd.read_csv(f, dtype=str), paths))
all_reports.to_csv('designite/all_reports.csv', index=False)
