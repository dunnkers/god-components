import unittest
from git_utils import get_commits

class TestSum(unittest.TestCase):
    def test_commits(self):
        commits = get_commits()
        self.assertTrue(len(commits) > 0)
        self.assertTrue('author' in commits.columns)
        self.assertTrue('email' in commits.columns)
        self.assertTrue('datetime' in commits.columns)
        self.assertTrue('message' in commits.columns)
        self.assertTrue('jira' in commits.columns)

if __name__ == '__main__':
    unittest.main()
