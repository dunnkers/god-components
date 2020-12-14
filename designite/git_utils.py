import os
import subprocess
from io import StringIO
import pandas as pd

REPOSITORIES =      'designite/repositories'
if (not os.path.exists(REPOSITORIES)): os.makedirs(REPOSITORIES)

def repo(cpu):
    return '{}/tika-cpu_{}'.format(REPOSITORIES, cpu)

def clone_tika(cpu):
    if (os.path.exists(repo(cpu))): return
    subprocess.run(['git', 'clone', 'https://github.com/apache/tika.git',
        'tika-cpu_{}'.format(cpu)], cwd=REPOSITORIES)

def git_checkout(cpu, commit_id):
    clone_tika(cpu)
    if (os.path.exists('{}/.git/index.lock'.format(repo(cpu)))):
        subprocess.run(['rm', '-f', '.git/index.lock'], cwd=repo(cpu))
    subprocess.run(['git', 'reset', '--hard', 'HEAD'],  cwd=repo(cpu))
    subprocess.run(['git', 'clean', '-fd'],             cwd=repo(cpu))
    subprocess.run(['git', 'checkout', commit_id],      cwd=repo(cpu))

def get_commits():
    file = 'designite/output/all_commits.csv'
    if (os.path.exists(file)):
        return pd.read_csv(file)
    git_checkout(1, 'main')
    subprocess.run(['git', 'pull'], cwd=repo(1))
    commit_ids = subprocess.check_output(['git', 'log', 
        '--pretty=format:%H%x09%an%x09%aD%x09%s'],
        encoding='utf-8', cwd=repo(1))
    stringio = StringIO(commit_ids)
    commits = pd.read_csv(stringio, sep='\t', header=None, names=[
        'id', 'author', 'datetime', 'message'
    ], parse_dates=['datetime'])
    commits['jira'] = commits['message'].str.extract('(TIKA-[0-9]{1,})')
    commits.to_csv(file, index=False)
    return commits
