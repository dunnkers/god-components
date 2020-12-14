import os
import pandas as pd
from git_utils import get_commits
import seaborn as sns
import matplotlib.pyplot as plt

all_reports = pd.read_csv('designite/output/all_reports.csv')
commits = get_commits()
data = commits.merge(all_reports, left_on='id', right_on='commit')
sns.lineplot(data=data, x='datetime', y='metric', hue='package')
plt.show()
print('end')