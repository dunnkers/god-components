import os
import pandas as pd
from git_utils import get_commits
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

all_locs = pd.read_csv('designite/output/all_locs.csv', dtype={
    'additions': 'float',
    'deletions': 'float'
}, parse_dates=['datetime'])

# Compute LOC change for every godcomp
godcomp_dfs = []
for godcomp, df in all_locs.groupby('godcomp'):
    print(godcomp, '...')
    df = df.sort_values('datetime')
    df['change'] = df['additions'] - df['deletions']
    df['LOC'] = df['change'].cumsum()
    godcomp_dfs.append(df)
data = pd.concat(godcomp_dfs)

# Commits that most contributed to deletions/additions
selected = []
for godcomp, df in data.groupby('godcomp'):
    # Commits that most contributed to deletions/additions
    selected.append(df.sort_values('change', ascending=True)[:5].copy())
    selected.append(df.sort_values('change', ascending=False)[:5].copy())
    # ^ e.g. top 5 commits
pd.concat(selected).to_csv('designite/output/top_5_commits-gc-buildup.csv',
    index=False)

# Plot
fig, ax = plt.subplots()
ax.set(yscale="log")
palette = sns.color_palette('tab10', len(godcomp_dfs))
sns.lineplot(data=data, x='datetime', y='LOC', hue='godcomp',
                ax=ax, palette=palette)
plt.show()
print('end')