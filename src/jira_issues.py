import requests
import pandas as pd
from tqdm import tqdm
import math

API = 'https://issues.apache.org/jira/rest/api/latest/search?jql=project=TIKA'
per_request = 50

def grab_issues(maxResults, startAt):
    url = '{}&maxResults={}&startAt={}'.format(API, maxResults, startAt)
    return requests.get(url).json()

def grab_index():
    url = '{}&maxResults=0'.format(API)
    return requests.get(url).json()

def map_issue(issue):
    comps = map(lambda comp: comp['name'], issue['fields']['components'])
    f = issue['fields']
    get_name = lambda prop: f[prop]['name'] if f[prop] else None
    return {
        'id':               issue['id'],
        'self':             issue['self'],
        'jira':             issue['key'],
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
        'summary':          f['summary'],
        'components':       ';'.join(comps)
    }

def get_issues(maxResults, startAt):
    issues = grab_issues(maxResults, startAt)['issues']
    return list(map(map_issue, issues))

# Fetch Jira issues and store in a .csv file
index = grab_index()
n_requests = math.ceil(index['total'] / per_request)
all_issues = []
for i in tqdm(range(n_requests)):
    issues = get_issues(per_request, per_request * i)
    all_issues += issues
df = pd.DataFrame(all_issues)
df.to_csv('output/all_issues.csv', index=False)

