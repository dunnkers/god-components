import os
import pandas as pd
from git_utils import get_commits
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

all_locs = pd.read_csv('designite/output/all_locs.csv', dtype={
    'additions': 'Int64',
    'deletions': 'Int64'
})
for godcomp, df in all_locs.groupby('godcomp'):
        
    df2 = df.sort_values('datetime')
    df['additions'] = df['additions'].cumsum()
    df['deletions'] = all_locs['deletions'].cumsum()
# sns.lineplot(data=data, x='datetime', y='metric', hue='package')
# plt.show()
print('end')