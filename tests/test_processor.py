import pytest
from src.processor import validate_data, calculate_metrics


def test_validate_data_valid():
    """
    Valid data validation test
    """
    record = {
        "voltage": 25.0,
        "current": 5.0,
        "temperature": 30.0,
        "power": 125.0
    }
    assert validate_data(record) is True


def test_validate_data_invalid_voltage():
    """
    Invalid data detection test (over-voltage)
    """
    record = {
        "voltage": 50.0,  # invalid voltage
        "current": 5.0,
        "temperature": 30.0,
        "power": 250.0
    }
    assert validate_data(record) is False


def test_calculate_metrics_accuracy():
    """
    Metric calculation accuracy test
    """
    data = [
        {
            "voltage": 20.0,
            "current": 2.0,
            "temperature": 25.0,
            "power": 40.0,
            "timestamp": "2025-01-15T10:00:00"
        },
        {
            "voltage": 30.0,
            "current": 4.0,
            "temperature": 35.0,
            "power": 120.0,
            "timestamp": "2025-01-15T10:05:00"
        }
    ]

    metrics = calculate_metrics(data)

    assert metrics["voltage"]["avg"] == 25.0
    assert metrics["voltage"]["min"] == 20.0
    assert metrics["voltage"]["max"] == 30.0

    assert metrics["current"]["avg"] == 3.0
    assert metrics["current"]["max"] == 4.0

    assert metrics["temperature"]["avg"] == 30.0
    assert metrics["total_energy_kwh"] > 0



# Add more tests as you see fit
# Good tests demonstrate you understand the code and edge cases
