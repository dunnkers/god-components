import requests
import pandas as pd
from tqdm import tqdm

def get_issue(n):
    url = 'https://issues.apache.org/jira/rest/api/latest/issue/TIKA-{}'.format(n)
    response = requests.get(url)
    issue = response.json()
    if 'errorMessages' in issue:
        print('error', n)
        return None
    else:
        comps = map(lambda comp: comp['name'], issue['fields']['components'])
        f = issue['fields']
        get_name = lambda prop: f[prop]['name'] if f[prop] else None
        return {
            'id':               issue['id'],
            'self':             issue['self'],
            'key':              issue['key'],
            'resolution':       get_name('resolution'),
            'priority':         get_name('priority'),
            'assignee':         get_name('assignee'),
            'status':           get_name('status'),
            'creator':          get_name('creator'),
            'reporter':         get_name('reporter'),
            'issuetype':        get_name('issuetype'),
            'resolutiondate':   f['resolutiondate'],
            'created':          f['created'],
            'updated':          f['updated'],
            'description':      f['description'],
            'components':       ';'.join(comps)
        }

issues = []
# use https://issues.apache.org/jira/rest/api/latest/search?jql=project=TIKA&maxResults=1000
for i in tqdm(range(1, 3500)):
    issue = get_issue(i)
    if not issue:
        continue
    issues.append(issue)
data = pd.DataFrame(issues)
data.to_csv('designite/output/jira.csv', index=False)

