import os
import pandas as pd
import glob

# Combine all reports into 1 .csv file
all_reports = []
for path in glob.glob('designite/reports/*.csv'):
    try:
        report = pd.read_csv(path, dtype=str)
        all_reports.append(report)
    except:
        print('Corrupted report: {}'.format(path))
all_reports = pd.concat(all_reports)
all_reports.to_csv('designite/all_reports.csv', index=False)
