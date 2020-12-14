import os
from time import time
import pandas as pd
import subprocess
import multiprocessing
import argparse
import numpy as np
from git_utils import get_commits, repo, git_checkout

# Settings
KEY = os.environ.get('DESIGNITE_ENTERPRISE')
RUNTIME =           'designite/runtime'
RUNTIME_JAR =       'designite/runtime/DesigniteJava_Enterprise.jar'
RUNTIME_CONFIG =    'designite/runtime/.config'
OUTPUT_FOLDER =     'designite/reports'
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
if (not os.path.exists(RUNTIME_CONFIG)):
    os.system('{} -r {}'.format(jar, KEY))
# Make dirs
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
    cpu, _ = multiprocessing.Process()._identity
    print('Running Designite for {} [cpu #{}]'.format(commit_id, cpu))
    git_checkout(cpu, commit_id)

    # Run Designite and remove reports folder
    start = time()
    targetfolder =  '{}/{}'.format(OUTPUT_FOLDER, commit_id)
    os.system('{} -i {} -o {}'.format(jar, repo(cpu), targetfolder))
    print('Designite ran for {:.2f} seconds'.format(time() - start))
    archsmells = pd.read_csv('{}/ArchitectureSmells.csv'.format(targetfolder))
    os.system('rm -rf {}'.format(targetfolder)) # Remove report

    # Map and save to .csv
    report = map_designite_output(archsmells, commit_id)
    targetfile =    '{}.csv'.format(targetfolder)
    report.to_csv(targetfile, index=False)

def not_yet_computed(commit_id):
    targetfolder =  '{}/{}'.format(OUTPUT_FOLDER, commit_id)
    targetfile =    '{}.csv'.format(targetfolder)
    return not os.path.exists(targetfile)

# Grab tags and run Designite
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find God Components w/ Designite.')
    parser.add_argument('--cpus')
    args = parser.parse_args()
    cpus = int(args.cpus or os.environ.get('SLURM_JOB_CPUS_PER_NODE', \
                                        multiprocessing.cpu_count()))
    print('Using {} cores.'.format(cpus))

    # get commits to compute
    commits = get_commits()
    commit_ids = commits['id'].values
    commits_to_compute = list(filter(not_yet_computed, commit_ids))
    print('Skipping {} commit ids.'.format(
        len(commit_ids) - len(commits_to_compute)))

    # Run Designite on all cores
    pool = multiprocessing.Pool(processes=cpus)
    pool.map(run_designite, commits_to_compute)
    pool.close()
    pool.join()