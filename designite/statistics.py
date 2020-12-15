import pandas as pd
from git_utils import get_commits

all_reports = pd.read_csv('designite/output/all_reports.csv')
commits = get_commits()
data = commits.merge(all_reports, left_on='id', right_on='commit')


# GC lifetime
dt = data.groupby('package')['datetime']
dtmin=dt.min()
dtmax=dt.max()
dtmindt=pd.to_datetime(dtmin,utc=True).dt.tz_convert('Europe/Amsterdam')
dtmaxdt=pd.to_datetime(dtmax,utc=True).dt.tz_convert('Europe/Amsterdam')
n_commits = data2.count()
days = (data444-data333).dt.days
pd.DataFrame([data3,data4,n_commits,days])\
    .transpose()\
    .reset_index()\
    .to_csv('designite/output/gcs-lifetime.csv',index=False)