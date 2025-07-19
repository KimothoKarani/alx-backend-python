#!/usr/bin/env python3
"""
A GitHub organization client.
"""
from typing import List, Dict
from utils import get_json, memoize


class GithubOrgClient:
    """
    A client for interacting with the GitHub API for a specific organization.
    """
    ORG_URL = "https://api.github.com/orgs/{org}"

    def __init__(self, org_name: str) -> None:
        """
        Initializes the GithubOrgClient.

        Args:
            org_name (str): The name of the GitHub organization.
        """
        self._org_name = org_name

    @memoize
    def org(self) -> Dict:
        """
        Fetches and memoizes the organization's data from the GitHub API.

        Returns:
            Dict: A dictionary containing the organization's data.
        """
        return get_json(self.ORG_URL.format(org=self._org_name))

    @property
    def _public_repos_url(self) -> str:
        """
        Returns the URL for the organization's public repositories.

        Returns:
            str: The URL string for public repos.
        """
        return self.org["repos_url"]

    @memoize
    def repos_payload(self) -> List[Dict]:
        """
        Fetches and memoizes the list of repositories for the organization.

        Returns:
            List[Dict]: A list of dictionaries, where each dictionary
                        represents a repository.
        """
        return get_json(self._public_repos_url)

    def public_repos(self, license: str = None) -> List[str]:
        """
        Returns a list of public repository names, optionally filtered by license.

        Args:
            license (str, optional): The license key to filter by (e.g., "apache-2.0").
                                     Defaults to None.

        Returns:
            List[str]: A list of repository names.
        """
        json_payload = self.repos_payload
        public_repos = [
            repo["name"] for repo in json_payload
            if license is None or self.has_license(repo, license)
        ]
        return public_repos

    @staticmethod
    def has_license(repo: Dict[str, Dict], license_key: str) -> bool:
        """
        Checks if a repository has a specific license.

        Args:
            repo (Dict[str, Dict]): The repository dictionary from the API.
            license_key (str): The license key to check for (e.g., "mit").

        Returns:
            bool: True if the repository has the specified license, False otherwise.
        """
        assert license_key is not None, "license_key cannot be None"
        try:
            license_info = repo.get("license", {})
            if license_info and license_info.get("key") == license_key:
                return True
        except KeyError:
            return False
        return False
