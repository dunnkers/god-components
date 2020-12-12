import os
from time import time
import pandas as pd
import subprocess
import multiprocessing

# Settings
KEY = os.environ.get('DESIGNITE_ENTERPRISE')
RUNTIME_JAR = 'designite/DesigniteJava_Enterprise.jar'
REPOSITORIES = 'designite/repositories'
OUTPUT_FOLDER = 'designite/reports'
# Vars
jar = 'java -jar {}'.format(RUNTIME_JAR)

# We require a license key
if (not KEY): exit('No Designite Enterprise key! See README to configure.')
# Register license if not registered yet
if (not os.path.exists('designite/.config')):
    os.system('{} -r {}'.format(jar, KEY))

# Run Designite on the currently checked out tag
def designite(output_folder, repo):
    # Run Designite
    start = time()
    os.system('{} -i {} -o {}'.format(jar, repo, output_folder))
    print('Designite ran for {:.2f} seconds'.format(time() - start))

    # Filter results for God Components
    archsmells = pd.read_csv('{}/ArchitectureSmells.csv'.format(
        output_folder))
    godcomps = archsmells[archsmells['Architecture Smell'] == 'God Component'].copy()
    os.system('rm -rf {}'.format(output_folder)) # Remove report
    return godcomps

def run_designite(commit_id):
    targetfile = '{}/{}.csv'.format(OUTPUT_FOLDER, commit_id)
    cpu, _ = multiprocessing.Process()._identity
    if (os.path.exists(targetfile)):
        print('Skipping {} [cpu #{}]'.format(commit_id, cpu))
        return
    print('Running Designite for {} [cpu #{}]'.format(commit_id, cpu))
    clone_tika(cpu)
    subprocess.run(['git', 'checkout', commit_id], cwd=repo(cpu))
    godcomps = designite('{}/{}'.format(OUTPUT_FOLDER, commit_id), repo(cpu))
    godcomps['Commit ID'] = commit_id
    godcomps.to_csv(targetfile, index=False)

def repo(cpu):
    return '{}/tika-cpu_{}'.format(REPOSITORIES, cpu)

def clone_tika(cpu):
    if (os.path.exists(repo(cpu))): return
    subprocess.run(['git', 'clone', 'https://github.com/apache/tika.git',
        'tika-cpu_{}'.format(cpu)], cwd=REPOSITORIES)

# Grab tags and run Designite
if __name__ == '__main__':
    cpus = int(os.environ.get('SLURM_JOB_CPUS_PER_NODE', \
                            multiprocessing.cpu_count()))
    cpus = 2
    if (not os.path.exists(REPOSITORIES)): os.makedirs(REPOSITORIES)

    # list all available tags on cpu_1 repo
    clone_tika(1)
    # tags = subprocess.check_output(['git', 'tag', '-l'],
    #     cwd='{}/tika-cpu_1'.format(REPOSITORIES), encoding='utf-8').splitlines()
    subprocess.run(['git', 'checkout', 'main'], cwd=repo(1))
    subprocess.run(['git', 'pull'], cwd=repo(1))
    commit_ids = subprocess.check_output(['git', 'log', '--pretty=format:%h'],
        cwd=repo(1), encoding='utf-8').splitlines()
    print('Using {} cores.'.format(cpus))

    # Run Designite on all cores
    pool = multiprocessing.Pool(processes=cpus)
    pool.map(run_designite, commit_ids)
    pool.close()
    pool.join()

    # Combine all reports into 1 .csv file
    paths = map(lambda f: os.path.join(OUTPUT_FOLDER, f), os.listdir(OUTPUT_FOLDER))
    all_reports = pd.concat(map(lambda f: pd.read_csv(f, dtype=str), paths))
    all_reports.to_csv('designite/all_reports.csv', index=False)
