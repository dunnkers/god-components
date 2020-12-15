import os
import pandas as pd
from git_utils import get_commits
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

all_locs = pd.read_csv('designite/output/all_locs.csv', dtype={
    'additions': 'float',
    'deletions': 'float'
})
for godcomp, df in all_locs.groupby('godcomp'):
        
    df = df.sort_values('datetime')
    df['change'] = df['additions'] - df['deletions']
    df['LOC'] = df['change'].cumsum()
    sns.lineplot(data=df, x='datetime', y='LOC', hue='godcomp')
    plt.show()
    print('end')
    break
# sns.lineplot(data=data, x='datetime', y='metric', hue='package')
# plt.show()
print('end')