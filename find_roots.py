import os
import pandas
import subprocess

TIKA_REPO = '../tika'
OUTPUT_FOLDER = 'designite/rooted'
MCS_FOLDER = 'designite/mcs'
NCS_FOLDER = 'designite/ncs'

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
    if len(candidates) == 1:
        print('✔ {} matched.'.format(package))
        df['root'] = candidates[0]
        df.to_csv(targetfile, index=False)
    elif len(candidates) > 1:
        print('❓ {} multiple candidates found.'.format(package))
        df_mc = pandas.DataFrame({ # 'multiple candidates' df
            'candidates': candidates,
            'Package Name': package
        }).merge(df)
        df_mc.to_csv('{}/{}-{}.csv'.format(MCS_FOLDER, tag, package), 
            index=False)
    elif len(candidates) == 0:
        print('❌ {} no candidates found.'.format(package))
        df.to_csv('{}/{}-{}.csv'.format(NCS_FOLDER, tag, package), 
            index=False)

# Combine all roots into 1 .csv file
roots = []
for rootfile in os.listdir(OUTPUT_FOLDER):
    rootpath = '{}/{}'.format(OUTPUT_FOLDER, rootfile)
    root = pandas.read_csv(rootpath, dtype=str)
    roots.append(report)
all_roots = pandas.concat(roots)
all_roots.to_csv('designite/all_roots.csv', index=False)
