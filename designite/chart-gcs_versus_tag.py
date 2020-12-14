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

# Compute # God Components per tag
n_godcomps = []
for tag in tags:
    godcomps = data[data['Tag'] == tag].groupby('Package Name')
    n_godcomps.append(len(godcomps))

# Make line plot
df = pd.DataFrame({'# God Components': n_godcomps, 'Tag': tags})
sns.lineplot(data=df, x='Tag', y='# God Components', sort=False)

# Rotate labels
locs, labels = plt.xticks()
plt.setp(labels, rotation=45)
plt.show()