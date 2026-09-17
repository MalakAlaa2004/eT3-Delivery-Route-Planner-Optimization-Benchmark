"""
eT3 Technical Challenge 2026 - Delivery Route Planner
Main CLI Application
"""

import argparse
import sys
import json
from src.io_handler import load_deliveries, print_route_plan
from src.solvers.greedy import GreedySolver
from src.solvers.metaheuristics import SimulatedAnnealingSolver, GeneticAlgorithmSolver
from src.benchmark import run_benchmark, print_benchmark_report


def parse_args():
    parser = argparse.ArgumentParser(
        description="eT3 Delivery Route Planner - Organizes delivery requests into trips with 10kg vehicle limit."
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        default="data/sample.csv",
        help="Path to input delivery file (.csv or .json). Default: data/sample.csv"
    )
    parser.add_argument(
        "--algorithm", "-a",
        type=str,
        choices=["greedy", "sa", "ga", "compare"],
        default="greedy",
        help="Optimization algorithm: 'greedy' (core baseline), 'sa' (Simulated Annealing), 'ga' (Genetic Algorithm), or 'compare' (benchmark matrix). Default: greedy"
    )
    parser.add_argument(
        "--allow-cross-area",
        action="store_true",
        help="Allows the greedy solver to pack multiple areas in one trip to optimize capacity utilization."
    )
    parser.add_argument(
        "--export", "-e",
        type=str,
        default=None,
        help="Optional path to export the resulting route plan as JSON."
    )
    return parser.parse_args()


def export_plan_to_json(plan, output_filepath: str):
    data = {
        "algorithm": plan.algorithm_name,
        "execution_time_ms": plan.execution_time_ms,
        "total_trips": len(plan.trips),
        "total_deliveries_assigned": plan.total_deliveries_assigned,
        "total_weight_kg": plan.total_weight_delivered,
        "capacity_utilization_pct": plan.average_utilization_pct,
        "single_area_purity_pct": round(plan.single_area_trip_ratio * 100, 1),
        "trips": [
            {
                "trip_id": t.trip_id,
                "total_weight_kg": t.total_weight,
                "remaining_capacity_kg": t.remaining_capacity,
                "top_priority": t.min_priority,
                "areas": sorted(list(t.areas)),
                "deliveries": [
                    {
                        "id": d.id,
                        "area": d.area,
                        "priority": d.priority,
                        "weight_kg": d.weight
                    }
                    for d in t.deliveries
                ]
            }
            for t in plan.trips
        ],
        "unassigned_deliveries": [
            {
                "id": d.id,
                "area": d.area,
                "priority": d.priority,
                "weight_kg": d.weight,
                "reason": reason
            }
            for d, reason in plan.unassigned
        ]
    }
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Exported route plan successfully to: {output_filepath}")


def main():
    args = parse_args()

    print("\n" + "=" * 76)
    print("eT3 Internship Technical Challenge 2026 - Delivery Route Planner")
    print(f"Loading input from: {args.input}")
    print("=" * 76)

    try:
        deliveries = load_deliveries(args.input)
    except Exception as err:
        print(f"[Error] Failed to read input file: {err}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(deliveries)} total delivery record(s).")

    if args.algorithm == "compare":
        benchmark_data = run_benchmark(deliveries)
        print_benchmark_report(benchmark_data)
        # Also show the greedy route plan as the primary baseline reference
        print("Primary Baseline Route Plan:")
        print_route_plan(benchmark_data["results"][0]["plan"])
        if args.export:
            export_plan_to_json(benchmark_data["results"][0]["plan"], args.export)
        return

    # Single solver execution
    if args.algorithm == "greedy":
        solver = GreedySolver(allow_cross_area_fill=args.allow_cross_area)
    elif args.algorithm == "sa":
        solver = SimulatedAnnealingSolver()
    elif args.algorithm == "ga":
        solver = GeneticAlgorithmSolver()
    else:
        print(f"[Error] Unknown algorithm: {args.algorithm}", file=sys.stderr)
        sys.exit(1)

    plan = solver.solve(deliveries)
    print_route_plan(plan)

    if args.export:
        export_plan_to_json(plan, args.export)


if __name__ == "__main__":
    main()
