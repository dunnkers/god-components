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

def map_commit(commit):
    output = subprocess.check_output([
        'git', 'diff', '--numstat', '{}~'.format(commit.id), commit.id],
        cwd=repo(1), encoding='utf-8')
    stringio = StringIO(output)
    df = pd.read_csv(stringio, sep='\t', header=None,
        names=['additions', 'deletions', 'file'])
    results = [] # result of what god components this commit affected
    for godcomp in godcomps:
        path = godcomp.replace('.', '/')
        files = df['file'].str.contains(path) # affected files
        if not files.any(): continue
        total = df[files].sum() # total LOC added/deleted
        total['godcomp'] = godcomp
        result = pd.concat([total, commit])
        results.append(result)
    new_df = pd.DataFrame(results)
    return new_df

mapped = commits.head(10).progress_apply(map_commit, axis=1)
mapped.to_csv('designite/output/all_locs.csv', index=False)
print('end')