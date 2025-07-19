#!/usr/bin/env python3
"""
A module for testing the utility functions in `utils.py`.
"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize
from typing import Mapping, Sequence, Any, Dict, Callable


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
        """
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)

        self.assertEqual(str(cm.exception), f"'{expected_key}'")


class TestGetJson(unittest.TestCase):
    """
    A class to test the `get_json` function from the `utils` module.
    """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(
            self,
            test_url: str,
            test_payload: Dict,
            mock_requests_get: Mock
    ) -> None:
        """
        Tests that `utils.get_json` returns the expected dictionary from a
        mocked HTTP call.
        """
        # Configure the mock to return a specific payload
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_requests_get.return_value = mock_response

        # Call the function under test
        result = get_json(test_url)

        # Assert that the mocked get method was called once with the correct URL
        mock_requests_get.assert_called_once_with(test_url)

        # Assert that the output of get_json is equal to the test payload
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """
    A class to test the `memoize` decorator from the `utils` module.
    """

    def test_memoize(self) -> None:
        """
        Tests that when a method decorated with `memoize` is called multiple
        times, the underlying method is only called once.
        """

        class TestClass:
            """A test class with a memoized property."""

            def a_method(self):
                """A method that returns a fixed value."""
                return 42

            @memoize
            def a_property(self):
                """
                A property that is memoized. It calls `a_method`.
                """
                return self.a_method()

        # Use patch as a context manager to mock `a_method`
        with patch.object(TestClass, 'a_method', return_value=42) as mock_a_method:
            # Create an instance of the test class
            instance = TestClass()

            # Call the property twice
            result1 = instance.a_property
            result2 = instance.a_property

            # Assert that the results are correct
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)

            # Assert that the underlying method was only called once
            mock_a_method.assert_called_once()


if __name__ == '__main__':
    unittest.main()
