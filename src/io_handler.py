"""
File input/output handlers and CLI formatting tables for Delivery Route Planner.
Supports CSV and JSON formats seamlessly.
"""

import csv
import json
import os
from typing import List, Tuple
from src.models import Delivery, RoutePlan


def _normalize_header(header: str) -> str:
    """Normalizes header string for robust dictionary lookup."""
    return header.strip().lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")


def load_deliveries_from_csv(filepath: str) -> List[Delivery]:
    """
    Parses deliveries from a CSV file.
    Accepts various header styles:
    'ID,Area,Priority,Package Weight (kg)' or 'id,area,priority,package_weight'
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"CSV file not found: {filepath}")

    deliveries: List[Delivery] = []
    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        try:
            raw_headers = next(reader)
        except StopIteration:
            # Empty file
            return []

        header_map = {_normalize_header(h): idx for idx, h in enumerate(raw_headers)}

        # Find column indices
        id_col = next((header_map[k] for k in ["id", "delivery_id"] if k in header_map), None)
        area_col = next((header_map[k] for k in ["area", "delivery_area", "district"] if k in header_map), None)
        prio_col = next((header_map[k] for k in ["priority", "prio", "urgency"] if k in header_map), None)
        weight_col = next((header_map[k] for k in ["package_weight_kg", "package_weight", "weight_kg", "weight"] if k in header_map), None)

        if None in (id_col, area_col, prio_col, weight_col):
            raise ValueError(
                f"CSV headers missing required fields. Expected: ID, Area, Priority, Package Weight. Found: {raw_headers}"
            )

        seen_ids = set()
        for row_num, row in enumerate(reader, start=2):
            if not row or all(not cell.strip() for cell in row):
                continue  # Skip blank lines
            try:
                raw_id = row[id_col].strip()
                raw_area = row[area_col].strip()
                raw_prio = row[prio_col].strip()
                raw_weight = row[weight_col].strip()

                # Check for NaN / missing / null weight
                if raw_weight.lower() in ("nan", "null", "none", "", "na"):
                    print(f"[Warning] Delivery ID {raw_id} (row {row_num}) has NaN/missing package weight. Skipping record.")
                    continue

                try:
                    weight = float(raw_weight)
                except ValueError:
                    print(f"[Warning] Delivery ID {raw_id} (row {row_num}) has non-numeric weight '{raw_weight}'. Skipping record.")
                    continue

                import math
                if math.isnan(weight):
                    print(f"[Warning] Delivery ID {raw_id} (row {row_num}) has NaN package weight. Skipping record.")
                    continue

                d_id = int(raw_id)
                # Check for duplicate ID
                if d_id in seen_ids:
                    print(f"[Warning] Duplicate delivery ID #{d_id} detected in row {row_num} (Area: '{raw_area}'). Cleaning and skipping duplicate.")
                    continue

                prio = int(raw_prio)
                seen_ids.add(d_id)
                deliveries.append(Delivery(id=d_id, area=raw_area, priority=prio, weight=weight))
            except (ValueError, IndexError) as err:
                print(f"[Warning] Skipping malformed row {row_num}: {row} (Error: {err})")

    return deliveries


def load_deliveries_from_json(filepath: str) -> List[Delivery]:
    """
    Parses deliveries from a JSON file.
    Expects an array of objects with keys matching:
    {"id": ..., "area": ..., "priority": ..., "package_weight": ...}
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"JSON file not found: {filepath}")

    with open(filepath, mode="r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as err:
            raise ValueError(f"Invalid JSON file format in {filepath}: {err}")

    if not isinstance(data, list):
        raise ValueError(f"JSON root must be a list of deliveries, got {type(data)}")

    deliveries: List[Delivery] = []
    seen_ids = set()
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            print(f"[Warning] Skipping invalid delivery entry #{idx}: {item}")
            continue
        try:
            raw_id = item.get("id") or item.get("ID") or idx + 1
            area = str(item.get("area") or item.get("Area", "")).strip()
            prio = int(item.get("priority") or item.get("Priority", 2))

            # Fetch weight field
            raw_weight = item.get("package_weight")
            if raw_weight is None:
                raw_weight = item.get("Package Weight (kg)")
            if raw_weight is None:
                raw_weight = item.get("weight")

            # Check for NaN / null / missing weight
            if raw_weight is None or str(raw_weight).strip().lower() in ("nan", "null", "none", "", "na"):
                print(f"[Warning] Delivery item #{idx + 1} (ID: {raw_id}) has NaN/missing package weight. Skipping record.")
                continue

            try:
                weight = float(raw_weight)
            except (ValueError, TypeError):
                print(f"[Warning] Delivery item #{idx + 1} (ID: {raw_id}) has non-numeric weight '{raw_weight}'. Skipping record.")
                continue

            import math
            if math.isnan(weight):
                print(f"[Warning] Delivery item #{idx + 1} (ID: {raw_id}) has NaN package weight. Skipping record.")
                continue

            d_id = int(raw_id)
            # Check for duplicate ID
            if d_id in seen_ids:
                print(f"[Warning] Duplicate delivery ID #{d_id} detected at item #{idx + 1} (Area: '{area}'). Cleaning and skipping duplicate.")
                continue

            seen_ids.add(d_id)
            deliveries.append(Delivery(id=d_id, area=area, priority=prio, weight=weight))
        except (ValueError, TypeError) as err:
            print(f"[Warning] Skipping malformed delivery item #{idx}: {item} (Error: {err})")

    return deliveries


def load_deliveries(filepath: str) -> List[Delivery]:
    """Loads deliveries automatically detecting CSV or JSON based on file extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        return load_deliveries_from_json(filepath)
    elif ext in [".csv", ".txt"]:
        return load_deliveries_from_csv(filepath)
    else:
        raise ValueError(f"Unsupported file extension '{ext}'. Please provide a .csv or .json file.")


def print_route_plan(plan: RoutePlan) -> None:
    """Prints a beautiful, clear formatted summary of the planned trips."""
    print("=" * 76)
    print(f"DELIVERY ROUTE PLAN  [{plan.algorithm_name.upper()}]")
    print("=" * 76)

    if not plan.trips and not plan.unassigned:
        print("No deliveries to dispatch. Trip plan is empty.")
        print("=" * 76)
        return

    print(f"Total Trips Scheduled: {len(plan.trips)}")
    print(f"Total Packages Assigned: {plan.total_deliveries_assigned}")
    print(f"Total Weight: {plan.total_weight_delivered:.2f} kg")
    print(f"Average Fleet Capacity Utilization: {plan.average_utilization_pct:.1f}%")
    print(f"Single-Area Trip Purity: {plan.single_area_trip_ratio * 100:.0f}%")
    print(f"Solver Compute Time: {plan.execution_time_ms:.2f} ms")
    print("-" * 76)

    for trip in plan.trips:
        area_summary = ", ".join(sorted(trip.areas))
        print(f"Trip #{trip.trip_id:02d} | Weight: {trip.total_weight:4.1f}/10.0 kg | Top Priority: P{trip.min_priority} | Areas: [{area_summary}]")
        print("   Packages:")
        for d in trip.deliveries:
            print(f"     • ID: {d.id:3d} | Area: {d.area:<15} | Priority: P{d.priority} | Weight: {d.weight:4.1f} kg")
        print("   " + "-" * 60)

    if plan.unassigned:
        print("\n" + "!" * 76)
        print("UNASSIGNABLE DELIVERIES (Exceeds Vehicle 10kg Limit or Invalid):")
        print("!" * 76)
        for delivery, reason in plan.unassigned:
            print(f"   [REJECTED] ID {delivery.id} ({delivery.area}, {delivery.weight} kg, P{delivery.priority}): {reason}")
        print("   -> Flagged for Dedicated Heavy Vehicle / Freight Handling")
        print("!" * 76)

    print("=" * 76 + "\n")
