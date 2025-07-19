#!/usr/bin/env python3
"""
A module for testing the `client.GithubOrgClient` class.
"""
import unittest
from unittest.mock import patch, PropertyMock, MagicMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD
from typing import Dict, List


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
        known_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos"
        }

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
        repos_payload = [{"name": "repo1"}, {"name": "repo2"}]
        mock_get_json.return_value = repos_payload

        with patch(
                'client.GithubOrgClient._public_repos_url',
                new_callable=PropertyMock,
                return_value="https://api.github.com/orgs/google/repos"
        ) as mock_public_repos_url:
            client = GithubOrgClient("google")
            public_repos = client.public_repos()

            expected_repos = ["repo1", "repo2"]
            self.assertEqual(public_repos, expected_repos)

            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self,
            repo: Dict,
            license_key: str,
            expected: bool
    ) -> None:
        """
        Tests the `has_license` static method with different inputs.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(('org_payload', 'repos_payload', 'expected_repos', 'apache2_repos'), TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration test for the `GithubOrgClient` class.
    This class uses fixtures to test the `public_repos` method, mocking
    only the external `requests.get` calls.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the class by patching `requests.get` to return example payloads
        from fixtures based on the requested URL.
        """

        # Define a side effect function for the mock to return different
        # payloads for different URLs.
        def side_effect(url):
            mock_response = MagicMock()
            if url == cls.org_payload["repos_url"]:
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = cls.org_payload
            return mock_response

        cls.get_patcher = patch('client.requests.get')
        mock_get = cls.get_patcher.start()
        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Tear down the class by stopping the patcher.
        """
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """
        Test the `public_repos` method without any license filter.
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """
        Test the `public_repos` method with a license filter.
        """
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == '__main__':
    unittest.main()
