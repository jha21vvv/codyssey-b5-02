"""Unit tests for MiniGitRepository."""

import unittest
from minigit.repository import MiniGitRepository


class TestMiniGitRepository(unittest.TestCase):
    def setUp(self):
        self.repo = MiniGitRepository()

    def test_uninitialized_operations_raise_runtime_error(self):
        with self.assertRaises(RuntimeError):
            self.repo.commit("initial")
        with self.assertRaises(RuntimeError):
            self.repo.branch("dev")
        with self.assertRaises(RuntimeError):
            self.repo.switch("dev")
        with self.assertRaises(RuntimeError):
            self.repo.log()

    def test_init_and_commit_flow(self):
        msg = self.repo.init("alice")
        self.assertIn("alice", msg)
        self.assertTrue(self.repo.is_initialized())

        c1, log1 = self.repo.commit("feat: initial commit")
        self.assertEqual(c1.author, "alice")
        self.assertEqual(c1.parents, [])

        c2, log2 = self.repo.commit("feat: second commit")
        self.assertEqual(c2.parents, [c1.hash])

        # Branches check
        self.assertEqual(self.repo.state.branches["main"], c2.hash)

    def test_branch_and_switch(self):
        self.repo.init("bob")
        c1, _ = self.repo.commit("first")

        self.repo.branch("feature")
        self.assertEqual(self.repo.state.branches["feature"], c1.hash)

        # Duplicate branch error
        with self.assertRaises(ValueError):
            self.repo.branch("feature")

        self.repo.switch("feature")
        self.assertEqual(self.repo.state.head_branch, "feature")

        c2, _ = self.repo.commit("feature commit")
        self.assertEqual(self.repo.state.branches["feature"], c2.hash)
        self.assertEqual(self.repo.state.branches["main"], c1.hash)

        # Unknown branch switch
        with self.assertRaises(KeyError):
            self.repo.switch("non_existent")

    def test_log_and_sorting(self):
        self.repo.init("charlie")
        c1, _ = self.repo.commit("alpha")
        c2, _ = self.repo.commit("beta")

        # Default log is topological (parents first)
        topological_commits = self.repo.log()
        self.assertEqual([c.hash for c in topological_commits], [c1.hash, c2.hash])

        # Sort by date
        date_sorted = self.repo.log(sort_by="date")
        self.assertEqual([c.hash for c in date_sorted], [c1.hash, c2.hash])

        # Sort by author
        author_sorted = self.repo.log(sort_by="author")
        self.assertEqual(len(author_sorted), 2)

    def test_path_and_ancestors(self):
        self.repo.init("dave")
        c1, _ = self.repo.commit("c1")
        c2, _ = self.repo.commit("c2")
        c3, _ = self.repo.commit("c3")

        path = self.repo.path(c1.hash, c3.hash)
        self.assertEqual(path, [c1.hash, c2.hash, c3.hash])

        ancestors_c3 = self.repo.ancestors(c3.hash)
        ancestor_hashes = [c.hash for c in ancestors_c3]
        self.assertIn(c1.hash, ancestor_hashes)
        self.assertIn(c2.hash, ancestor_hashes)

    def test_search(self):
        self.repo.init("elena")
        c1, _ = self.repo.commit("implement login endpoint")
        c2, _ = self.repo.commit("fix bug in user login")
        c3, _ = self.repo.commit("add logout feature")

        login_results = self.repo.search_keyword("login")
        self.assertEqual(len(login_results), 2)
        login_hashes = [c.hash for c in login_results]
        self.assertIn(c1.hash, login_hashes)
        self.assertIn(c2.hash, login_hashes)

        author_results = self.repo.search_author("elena")
        self.assertEqual(len(author_results), 3)


if __name__ == "__main__":
    unittest.main()
