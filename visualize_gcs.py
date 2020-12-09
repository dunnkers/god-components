import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import subprocess
from pkg_resources import parse_version

data = pd.read_csv('designite/all_commits.csv', dtype=str)

# Get git tags
TIKA_REPO = '../tika'
tags = subprocess.check_output(['git', 'tag', '-l'],
    cwd=TIKA_REPO, encoding='utf-8').splitlines()
tags = list(filter(lambda tag:
    tag != '0.1-incubating' and 
    tag != 'tika-1.3', tags))
tags.sort(key=parse_version) # Sort by semantic versioning
n_godcomps = []
for tag in tags:
    godcomps = data[data['Tag'] == tag].groupby('Package Name')
    n_godcomps.append(len(godcomps))
df = pd.DataFrame({'# God Components': n_godcomps, 'Tag': tags})
sns.lineplot(data=df, x='Tag', y='# God Components', sort=False)

# # Prepare data
# grouped = data.groupby(['Package Name', 'Tag']).count()
# grouped = grouped.sort_values(['Package Name', 'Tag'])
# grouped = grouped.diff()
# grouped['Commits made'] = grouped['CommitID'].replace(np.nan, 0).astype(int)
# grouped = grouped.reset_index()

# # Heatmap
# rectangular = pd.pivot_table(grouped,\
#     values='Commits made',\
#     index=['Package Name'],\
#     columns=['Tag'])
# g = sns.heatmap(rectangular,\
#     annot=True, linewidths=.5,\
#     cmap="YlGnBu", yticklabels=True)

# Rotate labels
locs, labels = plt.xticks()
plt.setp(labels, rotation=45)
plt.show()