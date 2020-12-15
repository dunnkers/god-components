import pandas as pd
from git_utils import get_commits, git_checkout, repo
import subprocess
from tqdm import tqdm
from io import StringIO
tqdm.pandas()

all_reports = pd.read_csv('designite/output/all_reports.csv')
godcomps = all_reports['package'].unique()

# loop every commit
commits = get_commits()
git_checkout(1, 'main')
subprocess.run(['git', 'pull'], cwd=repo(1))

def get_diff(commit_id):
    try:
        return subprocess.check_output([
            'git', 'diff', '--numstat', '{}~'.format(commit_id), commit_id],
            cwd=repo(1), encoding='utf-8')
    except:
        return ''

def get_locs(commit_id):
    output = get_diff(commit_id)
    stringio = StringIO(output)
    df = pd.read_csv(stringio, sep='\t', header=None,
        names=['additions', 'deletions', 'file'], dtype=str)
    df = df[df['additions'].str.isdigit()]
    df = df[df['deletions'].str.isdigit()]
    df = df[~df['file'].str.contains(' => ')]
    df['additions'] = pd.to_numeric(df['additions'])
    df['deletions'] = pd.to_numeric(df['deletions'])
    return df

def map_commit(commit):
    locdf = get_locs(commit.id)
    results = [] # result of what god components this commit affected
    for godcomp in godcomps:
        path = godcomp.replace('.', '/')
        files = locdf['file'].str.contains(path) # affected files
        if not files.any(): continue
        total = locdf[files].sum() # total LOC added/deleted
        total = total.drop(labels='file')
        total['godcomp'] = godcomp
        result = pd.concat([total, commit])
        results.append(result)
    new_df = pd.DataFrame(results)
    return new_df

mapped_commits = []
for index, row in tqdm(commits.iterrows(), total=commits.shape[0]):
    mapped_commits.append(map_commit(row))
all_locs = pd.concat(mapped_commits)
all_locs.to_csv('designite/output/all_locs.csv', index=False)
print('end')