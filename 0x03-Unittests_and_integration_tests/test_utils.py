#!/usr/bin/env python3
"""
A module for testing the `utils.access_nested_map` function.
"""
import unittest
from parameterized import parameterized
from utils import access_nested_map
from typing import Mapping, Sequence, Any


class TestAccessNestedMap(unittest.TestCase):
    """
    A class to test the `access_nested_map` function from the `utils` module.
    It uses parameterization to test various inputs.
    """
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(
            self,
            nested_map: Mapping,
            path: Sequence,
            expected: Any
    ) -> None:
        """
        Tests that `utils.access_nested_map` returns the expected result
        for various inputs.

        Args:
            nested_map (Mapping): The nested dictionary to access.
            path (Sequence): The path of keys to follow.
            expected (Any): The expected value at the end of the path.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)


if __name__ == '__main__':
    unittest.main()