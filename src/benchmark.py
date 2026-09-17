"""
Benchmarking engine for comparing Greedy, Simulated Annealing, and Genetic Algorithm solvers.
Generates comprehensive comparative performance matrices.
"""

from typing import List, Dict, Any
from src.models import Delivery, RoutePlan
from src.solvers.greedy import GreedySolver
from src.solvers.metaheuristics import SimulatedAnnealingSolver, GeneticAlgorithmSolver


def run_benchmark(deliveries: List[Delivery]) -> Dict[str, Any]:
    """Runs all three solvers on the same delivery dataset and collects comparative metrics."""
    solvers = [
        GreedySolver(name="Greedy (Baseline)"),
        SimulatedAnnealingSolver(name="Simulated Annealing (SA)"),
        GeneticAlgorithmSolver(name="Genetic Algorithm (GA)")
    ]

    results = []
    for solver in solvers:
        plan: RoutePlan = solver.solve(deliveries)
        results.append({
            "name": solver.name,
            "plan": plan,
            "trips": len(plan.trips),
            "utilization": plan.average_utilization_pct,
            "area_purity": round(plan.single_area_trip_ratio * 100, 1),
            "time_ms": round(plan.execution_time_ms, 2),
            "unassigned": len(plan.unassigned)
        })

    return {"results": results, "total_deliveries": len(deliveries)}


def print_benchmark_report(benchmark_data: Dict[str, Any]) -> None:
    """Formats and prints the comparative benchmark matrix."""
    results = benchmark_data["results"]
    print("\n" + "=" * 88)
    print(f"ALGORITHM BENCHMARK MATRIX (Evaluated on {benchmark_data['total_deliveries']} deliveries)")
    print("=" * 88)
    header = f"{'Algorithm':<28} | {'Trips':<6} | {'Utilization':<12} | {'Area Purity':<12} | {'Time (ms)':<10} | {'Unassigned'}"
    print(header)
    print("-" * 88)

    for r in results:
        line = (
            f"{r['name']:<28} | "
            f"{r['trips']:<6} | "
            f"{r['utilization']:>5.1f}%      | "
            f"{r['area_purity']:>5.1f}%      | "
            f"{r['time_ms']:>8.2f} ms | "
            f"{r['unassigned']}"
        )
        print(line)
    print("=" * 88 + "\n")
