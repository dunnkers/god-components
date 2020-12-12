import os
from time import time
import pandas as pd
import subprocess
import multiprocessing
import argparse
import numpy as np

# Settings
KEY = os.environ.get('DESIGNITE_ENTERPRISE')
RUNTIME_JAR = 'designite/DesigniteJava_Enterprise.jar'
REPOSITORIES = 'designite/repositories'
OUTPUT_FOLDER = 'designite/reports'
# Vars
jar = 'java -jar {}'.format(RUNTIME_JAR)
# God Component smell causes
SMELL_CAUSES = {
    'MANY_CLASSES': '''The tool detected the smell in this component because the 
component contains high number of classes. 
Number of classes in the component are: '''.replace('\n', '')
}

# We require a license key
if (not KEY): exit('No Designite Enterprise key! See README to configure.')
# Register license if not registered yet
if (not os.path.exists('designite/.config')):
    os.system('{} -r {}'.format(jar, KEY))
# Make dirs
if (not os.path.exists(REPOSITORIES)): os.makedirs(REPOSITORIES)
if (not os.path.exists(OUTPUT_FOLDER)): os.makedirs(OUTPUT_FOLDER)

def map_cause(cause):
    for key in SMELL_CAUSES:
        if SMELL_CAUSES[key] in cause:
            return key
    return 'OTHER'

def map_metric(cause):
    if SMELL_CAUSES['MANY_CLASSES'] in cause:
        return cause.replace(SMELL_CAUSES['MANY_CLASSES'], '')
    else:
        return np.nan

def map_designite_output(designite_output, commit_id):
    is_godcomp = designite_output['Architecture Smell'] == 'God Component'
    godcomps = designite_output[is_godcomp].copy()

    return pd.DataFrame({
        'commit':  commit_id,
        'repo':    godcomps['Project Name'],
        'package': godcomps['Package Name'],
        'smell':   godcomps['Architecture Smell'],
        'cause':   godcomps['Cause of the Smell'].transform(map_cause),
        'metric':  godcomps['Cause of the Smell'].transform(map_metric),
    })

def run_designite(commit_id):
    targetfolder =  '{}/{}'.format(OUTPUT_FOLDER, commit_id)
    targetfile =    '{}.csv'.format(targetfolder)
    cpu, _ = multiprocessing.Process()._identity
    if (os.path.exists(targetfile)):
        print('Skipping {} [cpu #{}]'.format(commit_id, cpu))
        return
    print('Running Designite for {} [cpu #{}]'.format(commit_id, cpu))
    subprocess.run(['rm', '-f', '.git/index.lock'], cwd=repo(cpu))
    clone_tika(cpu)
    subprocess.run(['git', 'reset', '--hard', 'HEAD'], cwd=repo(cpu))
    subprocess.run(['git', 'checkout', commit_id], cwd=repo(cpu))

    # Run Designite and remove reports folder
    start = time()
    os.system('{} -i {} -o {}'.format(jar, repo(cpu), targetfolder))
    print('Designite ran for {:.2f} seconds'.format(time() - start))
    archsmells = pd.read_csv('{}/ArchitectureSmells.csv'.format(targetfolder))
    os.system('rm -rf {}'.format(targetfolder)) # Remove report

    # Map and save to .csv
    report = map_designite_output(archsmells, commit_id)
    report.to_csv(targetfile, index=False)

def repo(cpu):
    return '{}/tika-cpu_{}'.format(REPOSITORIES, cpu)

def clone_tika(cpu):
    if (os.path.exists(repo(cpu))): return
    subprocess.run(['git', 'clone', 'https://github.com/apache/tika.git',
        'tika-cpu_{}'.format(cpu)], cwd=REPOSITORIES)

# Grab tags and run Designite
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find God Components w/ Designite.')
    parser.add_argument('--cpus')
    args = parser.parse_args()
    cpus = int(     args.cpus or 
                    os.environ.get('SLURM_JOB_CPUS_PER_NODE', \
                                        multiprocessing.cpu_count()))
    print('Using {} cores.'.format(cpus))

    # list all available tags on cpu_1 repo
    clone_tika(1)
    subprocess.run(['rm', '-f', '.git/index.lock'], cwd=repo(1))
    subprocess.run(['git', 'checkout', 'main'], cwd=repo(1))
    subprocess.run(['git', 'pull'], cwd=repo(1))
    commit_ids = subprocess.check_output(['git', 'log', '--pretty=format:%H'],
        cwd=repo(1), encoding='utf-8').splitlines()

    # Run Designite on all cores
    pool = multiprocessing.Pool(processes=cpus)
    pool.map(run_designite, commit_ids)
    pool.close()
    pool.join()

    # Combine all reports into 1 .csv file
    paths = map(lambda f: os.path.join(OUTPUT_FOLDER, f), os.listdir(OUTPUT_FOLDER))
    all_reports = pd.concat(map(lambda f: pd.read_csv(f, dtype=str), paths))
    all_reports.to_csv('designite/all_reports.csv', index=False)
