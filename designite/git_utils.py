import os
import subprocess
from io import StringIO
import pandas as pd

REPOSITORIES = 'designite/repositories'
if 'SLURM_JOB_CPUS_PER_NODE' in os.environ:
    REPOSITORIES = '/data/{}/repositories'.format(os.environ['USER'])
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

# Return array of commits by using `git log` command
def get_commits():
    file = 'designite/output/all_commits.csv'
    if (os.path.exists(file)):
        return pd.read_csv(file, parse_dates=['datetime'])
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

# Get commit # additions and # deletions using `git diff`
def get_locdata(commit_id):
    try:
        return subprocess.check_output([
            'git', 'diff', '--numstat', '{}~'.format(commit_id), commit_id],
            cwd=repo(1), encoding='utf-8')
    except:
        return ''

def get_locs(commit_id):
    output = get_locdata(commit_id)
    stringio = StringIO(output)
    df = pd.read_csv(stringio, sep='\t', header=None,
        names=['additions', 'deletions', 'file'], dtype=str)
    df = df[df['additions'].str.isdigit()]
    df = df[df['deletions'].str.isdigit()]
    df = df[~df['file'].str.contains(' => ')]
    df['additions'] = pd.to_numeric(df['additions'])
    df['deletions'] = pd.to_numeric(df['deletions'])
    return df

def compute_locs(godcomps, commit):
    # sort God Components by their nesting level, based on dots (.)
    # in this way the algorithm will check inclusion of more nested GC's first,
    # i.e. `    'org.apache.tika.parser.microsoft` will match before',
    #      `    'org.apache.tika.parser`',
    # so no duplicate matches appear.
    nesting_levels = list(map(lambda godcomp: godcomp.count('.'), godcomps))
    godcompsdf = pd.DataFrame({
        'package': godcomps,
        'nesting_level': nesting_levels
    })
    godcompsdf = godcompsdf.sort_values('nesting_level', ascending=False)

    # loop god components, only assign 1 file path to 1 GC at maximum.
    results = [] # result of what god components this commit affected
    locdf = get_locs(commit.id)
    all_files = locdf['file'].copy()
    for _, godcomp in godcompsdf.iterrows():
        # find files that affected this GC
        path = godcomp['package'].replace('.', '/')
        files = all_files.str.contains(path) # affected files
        if not files.any(): continue

        # prevent file path from being re-selected
        all_files = all_files.mask(files, '')

        # compute total Lines Of Code changed in all files affecting this GC
        total = locdf[files].sum() # total LOC added/deleted
        total = total.drop(labels='file')
        total['godcomp'] = godcomp['package']
        result = pd.concat([total, commit])
        results.append(result)
    new_df = pd.DataFrame(results)
    return new_df

# godcomps = [
#     'org.apache.tika.batch',
#     'org.apache.tika.detect',
#     'org.apache.tika.example',
#     'org.apache.tika.fork',
#     'org.apache.tika.metadata',
#     'org.apache.tika.mime',
#     'org.apache.tika.parser',
#     'org.apache.tika.parser.microsoft',
#     'org.apache.tika.parser.microsoft.chm',
#     'org.apache.tika.parser.microsoft.onenote',
#     'org.apache.tika.parser.microsoft.ooxml',
#     'org.apache.tika.parser.txt',
#     'org.apache.tika.sax',
#     'org.apache.tika.server',
#     'org.apache.tika.utils'
# ]
# commits = get_commits()

# mapped_commits = []
# from tqdm import tqdm
# for index, row in commits.iterrows():
#     mapped_commits.append(compute_locs(godcomps, row))
# all_locs = pd.concat(mapped_commits)
# print('end')
