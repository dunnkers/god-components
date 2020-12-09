import os
import pandas
import subprocess
import numpy as np

TIKA_REPO = '../tika'
OUTPUT_FOLDER = 'designite/rooted'
NCS_FOLDER = 'designite/ncs' # 'No candidates' folder

# Run some bash command and return its output
def run(cmd, input=''):
    print('Running', cmd, '...')
    result = subprocess.run(cmd.split(' '),
        stdout=subprocess.PIPE, cwd=TIKA_REPO, stdin=input)
    lines = result.stdout.split()
    return list(map(lambda s: s.decode('utf-8'), lines))

# Make output dirs
def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

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
    return candidates[index]

# All God Components
godcomps = pandas.read_csv('designite/all_reports.csv', dtype=str)

# Find folders associated to packages for certain tag/package
for obj, df in godcomps.groupby(['Tag', 'Package Name']):
    tag, package = obj
    targetfile = '{}/{}-{}.csv'.format(OUTPUT_FOLDER, tag, package)
    if (os.path.exists(targetfile)):
        print('Skipping tag {}, package {}'.format(tag, package))
        continue
    print('Parsing tag {}, package {}...'.format(tag, package))
    subprocess.run(['git', 'checkout', tag], cwd=TIKA_REPO)

    candidates = [] # Candidates for package match
    for root, subdirs, files in os.walk(TIKA_REPO):
        if not 'src' in root and 'target' in root:
            continue
        if not 'src/main' in root and 'src/test' in root:
            continue
        if not 'src/main/java' in root and 'src/main/resources' in root:
            continue
        if root.replace('/', '.').endswith(package):
            candidates.append(root)
    
    # Check whether match or not
    print('-> candidates:', candidates)
    mkdir(OUTPUT_FOLDER)
    if len(candidates) == 1:
        print('✔ {} matched.'.format(package))
        df['root'] = candidates[0]
        df.to_csv(targetfile, index=False)
    elif len(candidates) > 1:
        print('❓ {} multiple candidates found.'.format(package))
        df['root'] = chooseCandidate(candidates)
        df.to_csv(targetfile, index=False)
    elif len(candidates) == 0:
        print('❌ {} no candidates found.'.format(package))
        mkdir(NCS_FOLDER)
        df.to_csv('{}/{}-{}.csv'.format(NCS_FOLDER, tag, package), 
            index=False)

# Combine all roots into 1 .csv file
roots = []
for rootfile in os.listdir(OUTPUT_FOLDER):
    rootpath = '{}/{}'.format(OUTPUT_FOLDER, rootfile)
    root = pandas.read_csv(rootpath, dtype=str)
    roots.append(root)
all_roots = pandas.concat(roots)
all_roots.to_csv('designite/all_roots.csv', index=False)
