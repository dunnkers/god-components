import os
import pandas as pd
import subprocess

TIKA_REPO = '../tika'
OUTPUT_FOLDER = 'designite/commits'
roots = pd.read_csv('designite/all_roots.csv', dtype=str)

# Find commit id's
for obj, df in roots.groupby(['Tag', 'Package Name', 'root']):
    tag, package, root = obj
    targetfile = '{}/{}-{}.csv'.format(OUTPUT_FOLDER, tag, package)
    if (os.path.exists(targetfile)):
        print('Skipping tag {}, package {}'.format(tag, package))
        continue

    # Find commit ids
    subprocess.run(('git checkout '+tag).split(' '), cwd=TIKA_REPO)

    result = subprocess.run('git log --pretty=format:"%h" .'.split(' '),
        stdout=subprocess.PIPE, cwd=os.path.join(TIKA_REPO, root))
    lines = result.stdout.split()
    commit_ids = list(map(lambda s: s.decode('utf-8').replace('"', ''), lines))

    # Store
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    commits_gcs = pd.DataFrame({
        'CommitID':commit_ids,
        'Package Name': package
    }).merge(df)
    commits_gcs.to_csv(targetfile, index=False)

    print('end')


# Combine all commits into 1 .csv file
commits = []
for commitfile in os.listdir(OUTPUT_FOLDER):
    commitpath = '{}/{}'.format(OUTPUT_FOLDER, commitfile)
    commit = pd.read_csv(commitpath, dtype=str)
    commits.append(commit)
all_commits = pd.concat(commits)
all_commits.to_csv('designite/all_commits.csv', index=False)
