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
    It uses parameterization to test various inputs and expected exceptions.
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
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), 'a'),
        ({"a": 1}, ("a", "b"), 'b'),
    ])
    def test_access_nested_map_exception(
            self,
            nested_map: Mapping,
            path: Sequence,
            expected_key: str
    ) -> None:
        """
        Tests that `access_nested_map` raises a KeyError with a specific
        message for invalid paths.

        Args:
            nested_map (Mapping): The dictionary to access.
            path (Sequence): The invalid path of keys to follow.
            expected_key (str): The key that is expected to be missing.
        """
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)

        # Check that the exception message is the key that was not found
        self.assertEqual(str(cm.exception), f"'{expected_key}'")


if __name__ == '__main__':
    unittest.main()
