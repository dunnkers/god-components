import seaborn
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('designite/all_commits.csv', dtype=str)
view = data[data['Package Name'] == 'org.apache.tika.parser']
seaborn.countplot(x='Tag', data=view,
    order=view['Tag'].sort_values().unique())
locs, labels = plt.xticks()
plt.setp(labels, rotation=45)
plt.show()
print('end')