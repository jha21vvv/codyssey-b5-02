"""Unit tests for graph algorithms in Mini Git."""

import unittest
from minigit.graph import CommitGraph
from minigit.models import Commit


class TestCommitGraph(unittest.TestCase):
    def setUp(self):
        self.graph = CommitGraph()

    def test_topological_sort_linear(self):
        # A -> B -> C (A is parent of B, B is parent of C)
        cA = Commit(hash="cA", message="Root", author="Dev", timestamp=1.0, parents=[])
        cB = Commit(hash="cB", message="Child 1", author="Dev", timestamp=2.0, parents=["cA"])
        cC = Commit(hash="cC", message="Child 2", author="Dev", timestamp=3.0, parents=["cB"])

        self.graph.add_commit(cC)
        self.graph.add_commit(cA)
        self.graph.add_commit(cB)

        sorted_commits = self.graph.topological_sort()
        hashes = [c.hash for c in sorted_commits]

        # In topological sort, parents must always come before children
        self.assertEqual(hashes, ["cA", "cB", "cC"])

    def test_topological_sort_branch_and_merge(self):
        # cA -> cB -> cD
        #  \-> cC -/  (cD is merge commit having parents cB and cC)
        cA = Commit(hash="cA", message="A", author="Dev", timestamp=10.0, parents=[])
        cB = Commit(hash="cB", message="B", author="Dev", timestamp=20.0, parents=["cA"])
        cC = Commit(hash="cC", message="C", author="Dev", timestamp=30.0, parents=["cA"])
        cD = Commit(hash="cD", message="D", author="Dev", timestamp=40.0, parents=["cB", "cC"])

        for c in [cD, cC, cB, cA]:
            self.graph.add_commit(c)

        sorted_commits = self.graph.topological_sort()
        hashes = [c.hash for c in sorted_commits]

        # cA must be before cB and cC; both cB and cC must be before cD
        self.assertEqual(hashes[0], "cA")
        self.assertTrue(hashes.index("cB") < hashes.index("cD"))
        self.assertTrue(hashes.index("cC") < hashes.index("cD"))
        self.assertEqual(hashes[-1], "cD")

    def test_shortest_path_simple_and_undirected(self):
        # c1 - c2 - c3
        c1 = Commit(hash="c1", message="1", author="Dev", timestamp=1.0, parents=[])
        c2 = Commit(hash="c2", message="2", author="Dev", timestamp=2.0, parents=["c1"])
        c3 = Commit(hash="c3", message="3", author="Dev", timestamp=3.0, parents=["c2"])

        for c in [c1, c2, c3]:
            self.graph.add_commit(c)

        # Child to parent direction
        p1 = self.graph.find_shortest_path("c3", "c1")
        self.assertEqual(p1, ["c3", "c2", "c1"])

        # Parent to child direction
        p2 = self.graph.find_shortest_path("c1", "c3")
        self.assertEqual(p2, ["c1", "c2", "c3"])

        # Same node
        self.assertEqual(self.graph.find_shortest_path("c2", "c2"), ["c2"])

    def test_shortest_path_no_path(self):
        # Disconnected commits
        c1 = Commit(hash="c1", message="1", author="Dev", timestamp=1.0, parents=[])
        c2 = Commit(hash="c2", message="2", author="Dev", timestamp=2.0, parents=[])

        self.graph.add_commit(c1)
        self.graph.add_commit(c2)

        self.assertIsNone(self.graph.find_shortest_path("c1", "c2"))

    def test_shortest_path_tie_break_lexicographical(self):
        # Diamond graph:
        #       c_start
        #      /       \
        #    c_nodeB   c_nodeA
        #      \       /
        #       c_end
        # Both paths have 2 hops: [c_start, c_nodeA, c_end] vs [c_start, c_nodeB, c_end]
        # Lexicographical comparison:
        # "c_start->c_nodeA->c_end" < "c_start->c_nodeB->c_end"
        # Should choose c_nodeA!
        start = Commit(hash="c_start", message="S", author="Dev", timestamp=1.0, parents=[])
        nodeA = Commit(hash="c_nodeA", message="A", author="Dev", timestamp=2.0, parents=["c_start"])
        nodeB = Commit(hash="c_nodeB", message="B", author="Dev", timestamp=2.0, parents=["c_start"])
        end = Commit(hash="c_end", message="E", author="Dev", timestamp=3.0, parents=["c_nodeA", "c_nodeB"])

        for c in [start, nodeA, nodeB, end]:
            self.graph.add_commit(c)

        path = self.graph.find_shortest_path("c_start", "c_end")
        self.assertEqual(path, ["c_start", "c_nodeA", "c_end"])

    def test_ancestors(self):
        # c1 <- c2 <- c3
        c1 = Commit(hash="c1", message="1", author="Dev", timestamp=1.0, parents=[])
        c2 = Commit(hash="c2", message="2", author="Dev", timestamp=2.0, parents=["c1"])
        c3 = Commit(hash="c3", message="3", author="Dev", timestamp=3.0, parents=["c2"])

        for c in [c1, c2, c3]:
            self.graph.add_commit(c)

        self.assertEqual(self.graph.get_ancestors("c1"), [])
        self.assertEqual(self.graph.get_ancestors("c2"), ["c1"])
        self.assertEqual(set(self.graph.get_ancestors("c3")), {"c1", "c2"})


if __name__ == "__main__":
    unittest.main()
