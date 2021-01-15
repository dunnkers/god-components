import unittest
from git_utils import get_commits, get_locs

class TestSum(unittest.TestCase):
    def test_commits(self):
        data = get_commits()
        self.assertTrue(len(data) > 0)
        self.assertTrue('author' in data.columns)
        self.assertTrue('email' in data.columns)
        self.assertTrue('datetime' in data.columns)
        self.assertTrue('message' in data.columns)
        self.assertTrue('jira' in data.columns)
        data.to_csv('output/all_commits.csv', index=False)

    def test_get_locs(self):
        # load commits and reports
        self.assertTrue(os.path.exists('output/all_commits.csv'))
        self.assertTrue(os.path.exists('output/all_reports.csv'))
        all_commits = pd.read_csv('output/all_commits.csv')
        all_reports = pd.read_csv('output/all_reports.csv')

        # compute LOC's
        data = get_locs(all_commits, all_reports)
        self.assertTrue(len(data) > 0)
        self.assertTrue('commit' in data.columns)
        self.assertTrue('package' in data.columns)
        self.assertTrue('additions' in data.columns)
        self.assertTrue('deletions' in data.columns)
        self.assertTrue('LOC' in data.columns)
        self.assertTrue('change' in data.columns)
        data.to_csv('output/all_locs.csv', index=False)

if __name__ == '__main__':
    unittest.main()
