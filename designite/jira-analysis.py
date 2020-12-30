import requests
from xml.etree import ElementTree

url = 'https://issues.apache.org/jira/rest/api/latest/issue/TIKA-1'

response = requests.get(url)
data = response.json()
print(data['fields']['issuetype']['name'])

# https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-get