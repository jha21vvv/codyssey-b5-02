"""Unit tests for MiniGit CLI interface and REPL parsing."""

import unittest
from minigit.cli import MiniGitCLI


class TestMiniGitCLI(unittest.TestCase):
    def setUp(self):
        self.cli = MiniGitCLI()

    def test_case_insensitive_commands(self):
        out = self.cli.execute_line("init alice")
        self.assertIn("alice", out)

        out2 = self.cli.execute_line("bRaNcH feature")
        self.assertIn("Created branch 'feature'", out2)

        out3 = self.cli.execute_line("sWiTcH feature")
        self.assertIn("Switched to branch 'feature'", out3)

    def test_quoted_arguments_with_spaces(self):
        self.cli.execute_line('INIT "Alice Cooper"')
        out = self.cli.execute_line('COMMIT "Add fancy login feature with OAuth"')
        self.assertIn("Add fancy login feature with OAuth", out)

        # Search with quotes
        search_out = self.cli.execute_line('SEARCH "fancy"')
        self.assertIn("Add fancy login feature with OAuth", search_out)

        # Author search
        author_out = self.cli.execute_line('SEARCH --author="Alice Cooper"')
        self.assertIn("Alice Cooper", author_out)

    def test_log_sorting_options(self):
        self.cli.execute_line("INIT bob")
        self.cli.execute_line('COMMIT "First"')
        self.cli.execute_line('COMMIT "Second"')

        log_default = self.cli.execute_line("LOG")
        self.assertIn("commit", log_default)

        log_date = self.cli.execute_line("LOG --sort-by=date")
        self.assertIn("commit", log_date)

        log_author = self.cli.execute_line("LOG --sort-by=author")
        self.assertIn("commit", log_author)

        log_invalid = self.cli.execute_line("LOG --sort-by=invalid")
        self.assertIn("Invalid args", log_invalid)

    def test_path_and_ancestors_commands(self):
        self.cli.execute_line("INIT charlie")
        out1 = self.cli.execute_line('COMMIT "c1"')
        # Extract hash: [main <hash>] c1
        h1 = out1.split()[1].rstrip("]")

        out2 = self.cli.execute_line('COMMIT "c2"')
        h2 = out2.split()[1].rstrip("]")

        path_out = self.cli.execute_line(f"PATH {h1} {h2}")
        self.assertEqual(path_out, f"{h1} -> {h2}")

        ancestors_out = self.cli.execute_line(f"ANCESTORS {h2}")
        self.assertIn(f"commit {h1}", ancestors_out)

        # No path
        self.cli.execute_line("INIT fresh_repo")
        c_fresh = self.cli.execute_line('COMMIT "fresh"').split()[1].rstrip("]")
        unknown_path = self.cli.execute_line(f"PATH {c_fresh} 99999999")
        self.assertIn("Unknown commit", unknown_path)

    def test_error_handling(self):
        cli_empty = MiniGitCLI()
        # Uninitialized repo
        res = cli_empty.execute_line("LOG")
        self.assertEqual(res, "Repository not initialized")

        # Invalid args
        res2 = self.cli.execute_line("INIT")
        self.assertIn("Invalid args", res2)

        # Unknown branch
        self.cli.execute_line("INIT user")
        res3 = self.cli.execute_line("SWITCH ghost")
        self.assertIn("Unknown branch: ghost", res3)

        # Exit
        res_exit = self.cli.execute_line("exit")
        self.assertEqual(res_exit, "BYE")
        res_quit = self.cli.execute_line("QUIT")
        self.assertEqual(res_quit, "BYE")

    def test_korean_and_unicode_handling(self):
        self.cli.execute_line('INIT "홍길동"')
        msg1 = self.cli.execute_line('COMMIT "기능추가: 로그인 및 인증 모듈 구현"')
        self.assertIn("기능추가: 로그인 및 인증 모듈 구현", msg1)

        search_res = self.cli.execute_line("SEARCH 로그인")
        self.assertIn("홍길동", search_res)

        author_res = self.cli.execute_line('SEARCH --author="홍길동"')
        self.assertIn("기능추가", author_res)


if __name__ == "__main__":
    unittest.main()

