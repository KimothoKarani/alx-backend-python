#!/usr/bin/env python3
"""
A module for testing the `client.GithubOrgClient` class.
"""
import unittest
from unittest.mock import patch, PropertyMock, MagicMock
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
    def test_org(self, org_name: str, mock_get_json: MagicMock) -> None:
        """
        Tests that `GithubOrgClient.org` calls `get_json` once with the
        correct URL.
        """
        client = GithubOrgClient(org_name)
        client.org
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self) -> None:
        """
        Tests that `_public_repos_url` property returns the correct URL based
        on the mocked `org` property.
        """
        known_payload = {"repos_url":
                             "https://api.github.com/orgs/google/repos"}

        with patch(
                'client.GithubOrgClient.org',
                new_callable=PropertyMock,
                return_value=known_payload
        ) as mock_org_property:
            client = GithubOrgClient("google")
            repos_url = client._public_repos_url
            self.assertEqual(repos_url, known_payload["repos_url"])
            mock_org_property.assert_called_once()

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: MagicMock) -> None:
        """
        Tests that `public_repos` returns the correct list of repository names
        based on a mocked payload from `get_json` and a mocked
        `_public_repos_url` property.
        """
        # Define the payload that get_json should return
        repos_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"}
        ]
        mock_get_json.return_value = repos_payload

        # Mock the _public_repos_url property
        with patch(
                'client.GithubOrgClient._public_repos_url',
                new_callable=PropertyMock,
                return_value="https://api.github.com/orgs/google/repos"
        ) as mock_public_repos_url:
            client = GithubOrgClient("google")

            # Call the method under test
            public_repos = client.public_repos()

            # Assert that the list of repos is what we expect
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(public_repos, expected_repos)

            # Assert that the mocked property was called once
            mock_public_repos_url.assert_called_once()

            # Assert that the mocked get_json was called once
            mock_get_json.assert_called_once()


if __name__ == '__main__':
    unittest.main()
