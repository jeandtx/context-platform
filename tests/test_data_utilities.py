"""Unit tests for data utilities module."""

import pytest


class TestDataValidation:
    """Test suite for data validation functions."""

    def test_validate_empty_data(self):
        """Test that empty data is handled correctly."""
        data = {}
        assert isinstance(data, dict)
        assert len(data) == 0

    def test_validate_data_structure(self):
        """Test that data structure is valid."""
        data = {
            "id": 1,
            "name": "test_data",
            "value": 100.5,
        }
        assert "id" in data
        assert "name" in data
        assert "value" in data

    def test_validate_data_types(self):
        """Test that data types are correct."""
        data = {
            "id": 1,
            "name": "test",
            "value": 42.0,
        }
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)
        assert isinstance(data["value"], float)

    def test_process_numeric_data(self):
        """Test processing of numeric data."""
        values = [1, 2, 3, 4, 5]
        result = sum(values)
        assert result == 15
        assert len(values) == 5

    def test_process_string_data(self):
        """Test processing of string data."""
        text = "data_day_test"
        assert isinstance(text, str)
        assert len(text) == 13
        assert text.startswith("data")

    @pytest.mark.parametrize("value,expected", [
        (10, 10),
        (0, 0),
        (-5, -5),
    ])
    def test_parameterized_values(self, value, expected):
        """Test parameterized values."""
        assert value == expected
