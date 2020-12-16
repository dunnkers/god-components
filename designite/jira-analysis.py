import requests

url = 'https://jira.atlassian.com/rest/api/latest/issue/TIKA-3178'

r = requests.get(url)
data = r.json()
print(data)

# https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-get