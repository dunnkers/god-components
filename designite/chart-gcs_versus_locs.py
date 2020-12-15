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

# Plot
fig, ax = plt.subplots()
ax.set(yscale="log")
palette = sns.color_palette('tab10', len(godcomp_dfs))
sns.lineplot(data=data, x='datetime', y='LOC', hue='godcomp',
                ax=ax, palette=palette)
plt.show()
print('end')