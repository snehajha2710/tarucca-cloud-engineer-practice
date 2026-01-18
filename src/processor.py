#!/usr/bin/env python3
"""
Tarucca IoT Sensor Data Processor
Processes solar panel sensor data and generates analytical metrics.

This is the main file you need to complete for the case study.

Author: Sneha
"""

import csv
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def validate_data(record: dict) -> bool:
    """
    Validate sensor readings are within acceptable physical ranges.

    Acceptable ranges for solar panel sensors:
    - voltage: 18V - 32V
    - current: 0A - 12A
    - temperature: -10°C to 80°C
    - power: >= 0
    """

    try:
        voltage = float(record["voltage"])
        current = float(record["current"])
        temperature = float(record["temperature"])
        power = float(record["power"])

        if not (18.0 <= voltage <= 32.0):
            return False
        if not (0.0 <= current <= 12.0):
            return False
        if not (-10.0 <= temperature <= 80.0):
            return False
        if power < 0:
            return False

        return True

    except (KeyError, ValueError, TypeError):
        return False


def calculate_metrics(data: List[dict]) -> Dict:
    """
    Calculate comprehensive metrics from sensor data.
    """

    voltages = [float(r["voltage"]) for r in data]
    currents = [float(r["current"]) for r in data]
    temperatures = [float(r["temperature"]) for r in data]
    powers = [float(r["power"]) for r in data]

    # Energy calculation (5-minute intervals)
    interval_hours = 5 / 60
    total_energy_kwh = sum(powers) * interval_hours / 1000

    # Peak power hour calculation
    hourly_power = {}
    for r in data:
        if "timestamp" in r:
            timestamp = datetime.fromisoformat(r["timestamp"])
            hour = timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_power.setdefault(hour, []).append(float(r["power"]))

    peak_hour = (
        max(hourly_power.items(), key=lambda item: sum(item[1]) / len(item[1]))[0]
        if hourly_power
        else None
    )

    return {
        "voltage": {
            "avg": round(statistics.mean(voltages), 2),
            "min": min(voltages),
            "max": max(voltages),
            "std": round(statistics.stdev(voltages), 2) if len(voltages) > 1 else 0.0,
        },
        "current": {
            "avg": round(statistics.mean(currents), 2),
            "min": min(currents),
            "max": max(currents),
        },
        "temperature": {
            "avg": round(statistics.mean(temperatures), 2),
            "min": min(temperatures),
            "max": max(temperatures),
        },
        "total_energy_kwh": round(total_energy_kwh, 2),
        "peak_power_hour": peak_hour.isoformat() if peak_hour else None,
    }


def process_sensor_data(input_file: str, output_dir: str = "data/processed") -> dict:
    """
    Main processing function - orchestrates the entire data pipeline.

    Enhancement Option A:
    - Gracefully handles corrupt / malformed CSV files
    - Outputs structured error JSON instead of crashing
    """

    result = {
        "input_file": Path(input_file).name,
        "output_file": None,
        "processed_at": datetime.utcnow().isoformat(),
        "status": "pending",
        "records_processed": 0,
        "records_invalid": 0,
        "metrics": {},
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    output_file = output_path / f"{Path(input_file).stem}_result.json"

    try:
        input_path = Path(input_file)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        valid_records = []

        with input_path.open(newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                try:
                    if validate_data(row):
                        valid_records.append(row)
                    else:
                        result["records_invalid"] += 1
                except Exception:
                    result["records_invalid"] += 1

        if not valid_records:
            raise ValueError("No valid records found in CSV")

        metrics = calculate_metrics(valid_records)

        result.update(
            {
                "status": "success",
                "records_processed": len(valid_records),
                "metrics": metrics,
                "output_file": output_file.name,
            }
        )

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    # Always write output JSON (success OR error)
    with output_file.open("w") as f:
        json.dump(result, f, indent=2)

    return result


def main():
    """
    CLI entry point - processes all CSV files in the incoming directory.
    """

    incoming_dir = Path("data/incoming")

    if not incoming_dir.exists():
        print(f"Error: Directory {incoming_dir} does not exist")
        return

    csv_files = list(incoming_dir.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in {incoming_dir}")
        print("Run: python src/data_generator.py")
        return

    print("=" * 60)
    print("TARUCCA DATA PROCESSOR")
    print("=" * 60)

    for csv_file in csv_files:
        print(f"Processing: {csv_file.name}")
        result = process_sensor_data(str(csv_file))

        if result["status"] == "success":
            print(f"Success: {result['records_processed']} records processed")
        else:
            print(f"Error: {result.get('error')}")

        print()

    print("=" * 60)
    print("Processing complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
