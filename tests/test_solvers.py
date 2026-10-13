"""
Unit tests for eT3 Delivery Route Planner.
Verifies all constraints, requirements, and edge cases from Section 3.2 and 3.4 of the challenge PDF.
"""

import unittest
import os
from src.models import Delivery, Trip, RoutePlan
from src.io_handler import load_deliveries_from_csv, load_deliveries_from_json
from src.solvers.greedy import GreedySolver
from src.solvers.metaheuristics import SimulatedAnnealingSolver, GeneticAlgorithmSolver


class TestDeliveryRoutePlanner(unittest.TestCase):
    def setUp(self):
        self.sample_csv = "data/sample.csv"
        self.sample_json = "data/sample.json"
        self.edge_cases_csv = "data/edge_cases.csv"

    def test_sample_csv_and_json_parity(self):
        """Verify that loading from CSV and JSON produce identical delivery requests."""
        csv_deliveries = load_deliveries_from_csv(self.sample_csv)
        json_deliveries = load_deliveries_from_json(self.sample_json)

        self.assertEqual(len(csv_deliveries), 5)
        self.assertEqual(len(json_deliveries), 5)

        for d_csv, d_json in zip(csv_deliveries, json_deliveries):
            self.assertEqual(d_csv.id, d_json.id)
            self.assertEqual(d_csv.area, d_json.area)
            self.assertEqual(d_csv.priority, d_json.priority)
            self.assertAlmostEqual(d_csv.weight, d_json.weight, places=2)

    def test_vehicle_capacity_hard_constraint(self):
        """Verify that NO trip ever exceeds the 10.0 kg vehicle capacity limit."""
        deliveries = load_deliveries_from_csv(self.sample_csv)
        solvers = [GreedySolver(), SimulatedAnnealingSolver(seed=123), GeneticAlgorithmSolver(seed=123)]

        for solver in solvers:
            plan = solver.solve(deliveries)
            for trip in plan.trips:
                self.assertLessEqual(
                    trip.total_weight,
                    10.0001,
                    f"Solver {solver.name} produced a trip (#{trip.trip_id}) exceeding 10 kg: {trip.total_weight} kg"
                )

    def test_every_valid_delivery_appears_exactly_once(self):
        """Verify that every valid package is assigned to exactly one trip."""
        deliveries = load_deliveries_from_csv(self.sample_csv)
        solvers = [GreedySolver(), SimulatedAnnealingSolver(seed=123), GeneticAlgorithmSolver(seed=123)]

        expected_ids = {d.id for d in deliveries}

        for solver in solvers:
            plan = solver.solve(deliveries)
            assigned_ids = []
            for trip in plan.trips:
                for d in trip.deliveries:
                    assigned_ids.append(d.id)

            self.assertEqual(
                len(assigned_ids),
                len(expected_ids),
                f"Solver {solver.name} did not assign the expected number of deliveries."
            )
            self.assertEqual(
                set(assigned_ids),
                expected_ids,
                f"Solver {solver.name} dropped or duplicated deliveries: {assigned_ids}"
            )

    def test_edge_case_empty_deliveries(self):
        """Verify sensible behavior when there are no deliveries."""
        solver = GreedySolver()
        plan = solver.solve([])

        self.assertEqual(len(plan.trips), 0)
        self.assertEqual(len(plan.unassigned), 0)
        self.assertEqual(plan.total_weight_delivered, 0.0)

    def test_edge_case_overweight_package(self):
        """Verify sensible behavior when a package exceeds 10 kg capacity."""
        overweight_pkg = Delivery(id=99, area="Maadi", priority=1, weight=14.5)
        normal_pkg = Delivery(id=100, area="Maadi", priority=1, weight=3.0)

        solver = GreedySolver()
        plan = solver.solve([overweight_pkg, normal_pkg])

        # Normal package assigned
        self.assertEqual(len(plan.trips), 1)
        self.assertEqual(plan.trips[0].deliveries[0].id, 100)

        # Overweight package rejected and recorded in unassigned
        self.assertEqual(len(plan.unassigned), 1)
        self.assertEqual(plan.unassigned[0][0].id, 99)
        self.assertIn("exceeds maximum vehicle capacity", plan.unassigned[0][1])

    def test_edge_case_exact_10kg_package(self):
        """Verify a package of exactly 10.0 kg is accepted and occupies exactly one full trip."""
        pkg = Delivery(id=50, area="Zamalek", priority=1, weight=10.0)
        solver = GreedySolver()
        plan = solver.solve([pkg])

        self.assertEqual(len(plan.trips), 1)
        self.assertEqual(plan.trips[0].total_weight, 10.0)
        self.assertEqual(plan.trips[0].remaining_capacity, 0.0)

    def test_edge_case_duplicate_priorities(self):
        """Verify that multiple deliveries with the same priority are grouped sensibly."""
        pkgs = [
            Delivery(id=1, area="Nasr City", priority=1, weight=3.0),
            Delivery(id=2, area="Nasr City", priority=1, weight=4.0),
            Delivery(id=3, area="Nasr City", priority=1, weight=2.0)
        ]
        solver = GreedySolver()
        plan = solver.solve(pkgs)

        # Total weight 9.0 kg <= 10.0 kg, same area, same priority -> all in 1 trip
        self.assertEqual(len(plan.trips), 1)
        self.assertEqual(len(plan.trips[0].deliveries), 3)
        self.assertEqual(plan.trips[0].total_weight, 9.0)

    def test_priority_urgency_dispatch_order(self):
        """Verify that trips with lower priority numbers (Priority 1) are ordered first."""
        deliveries = load_deliveries_from_csv(self.sample_csv)
        solver = GreedySolver()
        plan = solver.solve(deliveries)

        # First trips must contain Priority 1 items
        self.assertEqual(plan.trips[0].min_priority, 1)
        self.assertEqual(plan.trips[1].min_priority, 1)
        # Later trip has Priority 2 or 3
        self.assertGreaterEqual(plan.trips[2].min_priority, 2)

    def test_edge_case_duplicate_ids(self):
        """Verify that duplicate delivery IDs are detected, cleaned, and skipped."""
        pkgs = [
            Delivery(id=1, area="Maadi", priority=1, weight=2.0),
            Delivery(id=1, area="Maadi", priority=2, weight=3.0),  # Duplicate ID 1
            Delivery(id=2, area="Maadi", priority=1, weight=4.0)
        ]
        solver = GreedySolver()
        plan = solver.solve(pkgs)

        self.assertEqual(len(plan.trips), 1)
        self.assertEqual(len(plan.trips[0].deliveries), 2)
        assigned_ids = [d.id for d in plan.trips[0].deliveries]
        self.assertEqual(set(assigned_ids), {1, 2})
        # Duplicate is captured in unassigned
        self.assertEqual(len(plan.unassigned), 1)
        self.assertIn("Duplicate delivery ID", plan.unassigned[0][1])

    def test_edge_case_nan_weight(self):
        """Verify that packages with NaN or invalid weights are flagged and rejected."""
        import math
        nan_pkg = Delivery(id=99, area="Dokki", priority=1, weight=float("nan"))
        valid_pkg = Delivery(id=100, area="Dokki", priority=1, weight=3.5)

        solver = GreedySolver()
        plan = solver.solve([nan_pkg, valid_pkg])

        self.assertEqual(len(plan.trips), 1)
        self.assertEqual(plan.trips[0].deliveries[0].id, 100)
        self.assertEqual(len(plan.unassigned), 1)
        self.assertEqual(plan.unassigned[0][0].id, 99)
        self.assertIn("NaN", plan.unassigned[0][1])


if __name__ == "__main__":
    unittest.main()
