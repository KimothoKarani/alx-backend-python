#!/usr/bin/env python3
"""
A module for testing the `client.GithubOrgClient` class.
"""
import unittest
from unittest.mock import patch, PropertyMock
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
        """
        client = GithubOrgClient(org_name)
        client.org
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self):
        """
        Tests that `_public_repos_url` property returns the correct URL based
        on the mocked `org` property.
        """
        # The known payload that `org` should return
        known_payload = {"repos_url": "https://api.github.com/orgs/google/repos"}

        # Use patch as a context manager to mock the `org` property
        with patch(
                'client.GithubOrgClient.org',
                new_callable=PropertyMock,
                return_value=known_payload
        ) as mock_org_property:
            # Create an instance of the client
            client = GithubOrgClient("google")

            # Access the `_public_repos_url` property
            repos_url = client._public_repos_url

            # Assert that the URL is the one from our known payload
            self.assertEqual(repos_url, known_payload["repos_url"])

            # Assert that the `org` property was accessed once
            mock_org_property.assert_called_once()


if __name__ == '__main__':
    unittest.main()
