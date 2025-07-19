#!/usr/bin/env python3
"""
A module for testing the `client.GithubOrgClient` class.
"""
import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """
    A class to test the `GithubOrgClient` class from the `client` module.
    """
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """
        Tests that `GithubOrgClient.org` calls `get_json` once with the
        correct URL.

        Args:
            org_name (str): The organization name to test.
            mock_get_json (MagicMock): The mock object for `get_json`.
        """
        # Create an instance of the client
        client = GithubOrgClient(org_name)

        # Call the `org` property, which should trigger the memoized method
        client.org

        # Define the expected URL that should have been called
        expected_url = f"https://api.github.com/orgs/{org_name}"

        # Assert that the mocked get_json was called exactly once with the URL
        mock_get_json.assert_called_once_with(expected_url)


if __name__ == '__main__':
    unittest.main()
