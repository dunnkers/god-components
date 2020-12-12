import os
import pandas as pd
import subprocess
import numpy as np

TIKA_REPO = '../tika'
OUTPUT_FOLDER = 'designite/commits'

def getTotalLOC(candidate):
    files = subprocess.Popen('find {} -name *'.format(candidate).split(' '), 
        stdout=subprocess.PIPE)
    result = subprocess.Popen('xargs wc -l'.split(' '),
        stdout=subprocess.PIPE, stdin=files.stdout)
    out, _ = result.communicate()
    locs = out.split()
    loc = int(locs[len(locs) - 2])
    return loc

def chooseCandidate(candidates):
    locs = list(map(getTotalLOC, candidates))
    index = np.argmax(locs)
    return os.path.relpath(candidates[index], TIKA_REPO)

# Match Java package name to folder in git repository
def findCandidates(package):
    candidates = [] # Candidates for package match
    for root, _, _ in os.walk(TIKA_REPO):
        if not 'src' in root and 'target' in root:
            continue
        if not 'src/main' in root and 'src/test' in root:
            continue
        if not 'src/main/java' in root and 'src/main/resources' in root:
            continue
        if root.replace('/', '.').endswith(package):
            candidates.append(root)
    return candidates

# All God Components
godcomps = pd.read_csv('designite/all_reports.csv', dtype=str)

# Find folders associated to packages for certain tag/package
for obj, df in godcomps.groupby(['commit', 'package']):
    commit, package = obj
    targetfile = '{}/{}-{}.csv'.format(OUTPUT_FOLDER, commit, package)
    if (os.path.exists(targetfile)):
        print('Skipping commit {}, package {}'.format(commit, package))
        continue
    print('Parsing commit {}, package {}...'.format(commit, package))
    subprocess.run(['git', 'checkout', commit], cwd=TIKA_REPO)

    # Find candidates
    candidates = findCandidates(package)
    root = chooseCandidate(candidates) if candidates else None
    # Find commit ID's
    commit_ids = subprocess.check_output(['git', 'log', '--pretty=format:%h'],
        cwd=os.path.join(TIKA_REPO, root), encoding='utf-8').splitlines()

    # Export dataframe
    commits_gcs = pd.DataFrame({
        'CommitID': commit_ids,
        'Root': root,
        'Package Name': package # used for merge()
    }).merge(df)
    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
    commits_gcs.to_csv(targetfile, index=False)

# Combine all roots into 1 .csv file
paths = map(lambda f: os.path.join(OUTPUT_FOLDER, f), os.listdir(OUTPUT_FOLDER))
all_reports = pd.concat(map(lambda f: pd.read_csv(f, dtype=str), paths))
all_reports.to_csv('designite/all_commits.csv', index=False)
