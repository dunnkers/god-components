import os
from time import time
import pandas
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

# Run some bash command and return its output
def run(cmd):
    print('Running', cmd, '...')
    result = subprocess.run(cmd.split(' '),
        stdout=subprocess.PIPE, cwd=TIKA_REPO)
    lines = result.stdout.split()
    return list(map(lambda s: s.decode('utf-8'), lines))

# Run Designite on the currently checked out tag
def designite(output_folder):
    # Run Designite
    start = time()
    cmd = '{} -i {} -o {}'.format(jar, TIKA_REPO, output_folder)
    print('Executing `{}`...'.format(cmd))
    os.system(cmd)
    end = time()
    print('Designite ran for {:.2f} seconds'.format(end - start))

    # Filter results for God Components
    archsmells = pandas.read_csv('{}/ArchitectureSmells.csv'.format(
        output_folder))
    godcomps = archsmells[archsmells['Architecture Smell'] == 'God Component'].copy()
    os.system('rm -rf {}'.format(output_folder)) # Remove report
    return godcomps

# Grab tags
tags = run('git tag -l')
for tag in tags:
    targetfile = '{}/{}.csv'.format(OUTPUT_FOLDER, tag)
    if (os.path.exists(targetfile)):
        print('Skipping tag', tag)
        continue
    print('Running Designite for tag', tag)
    run('git checkout ' + tag)
    godcomps = designite('{}/{}'.format(OUTPUT_FOLDER, tag))
    godcomps['Tag'] = tag
    godcomps.to_csv(targetfile, index=False)

# Combine all reports into 1 .csv file
reports = []
for reportfile in os.listdir(OUTPUT_FOLDER):
    reportpath = '{}/{}'.format(OUTPUT_FOLDER, reportfile)
    report = pandas.read_csv(reportpath, dtype=str)
    reports.append(report)
all_reports = pandas.concat(reports)
all_reports.to_csv('designite/all_reports.csv', index=False)
