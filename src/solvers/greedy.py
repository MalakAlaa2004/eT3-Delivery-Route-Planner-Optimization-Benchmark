"""
Greedy Priority-Area Best-Fit Decreasing (BFD) Solver.
The core, deterministic baseline for the Delivery Route Planner.
"""

import time
from typing import List
from src.models import Delivery, Trip, RoutePlan
from src.solvers.base import BaseSolver


class GreedySolver(BaseSolver):
    """
    Deterministic Heuristic Solver:
    1. Filters and isolates overweight packages (> 10 kg).
    2. Sorts packages prioritizing urgency (Priority 1 before 2, 3),
       then clusters by Geographic Area, and orders by Weight descending (BFD).
    3. Allocates each package to an existing trip matching its area if capacity allows (<= 10 kg).
    4. If no same-area trip has room, opens a new trip to preserve spatial cohesion.
    5. Final pass sorts dispatched trips by urgency (min_priority ascending)
       so trips with Priority 1 orders are dispatched first.
    """

    def __init__(self, name: str = "Greedy Heuristic", max_capacity: float = 10.0, allow_cross_area_fill: bool = False):
        super().__init__(name=name, max_capacity=max_capacity)
        self.allow_cross_area_fill = allow_cross_area_fill

    def solve(self, deliveries: List[Delivery]) -> RoutePlan:
        start_time = time.perf_counter()

        valid_deliveries, unassignable = self.filter_and_validate(deliveries)

        if not valid_deliveries:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return RoutePlan(
                algorithm_name=self.name,
                trips=[],
                unassigned=unassignable,
                execution_time_ms=elapsed_ms
            )

        # Sorting: Priority ascending (urgent first), then Area alphabetically, then Weight descending
        sorted_deliveries = sorted(
            valid_deliveries,
            key=lambda d: (d.priority, d.area, -d.weight, d.id)
        )

        trips: List[Trip] = []
        trip_counter = 1

        for delivery in sorted_deliveries:
            assigned = False

            # Stage 1: Try to fit into an existing trip serving the SAME AREA (Best-Fit)
            best_same_area_trip = None
            min_remaining_space = float("inf")

            for trip in trips:
                if delivery.area in trip.areas and trip.can_fit(delivery, self.max_capacity):
                    space_after = trip.remaining_capacity - delivery.weight
                    if space_after < min_remaining_space:
                        min_remaining_space = space_after
                        best_same_area_trip = trip

            if best_same_area_trip is not None:
                best_same_area_trip.add_delivery(delivery)
                assigned = True

            # Stage 2: If cross-area fill is enabled, try any existing trip with space
            if not assigned and self.allow_cross_area_fill:
                best_any_trip = None
                min_remaining_space = float("inf")
                for trip in trips:
                    if trip.can_fit(delivery, self.max_capacity):
                        space_after = trip.remaining_capacity - delivery.weight
                        if space_after < min_remaining_space:
                            min_remaining_space = space_after
                            best_any_trip = trip
                if best_any_trip is not None:
                    best_any_trip.add_delivery(delivery)
                    assigned = True

            # Stage 3: If still not assigned, open a new trip
            if not assigned:
                new_trip = Trip(trip_id=trip_counter, deliveries=[delivery])
                trips.append(new_trip)
                trip_counter += 1

        # Sort trips to ensure trips with the most urgent deliveries (Priority 1) dispatch first
        trips.sort(key=lambda t: (t.min_priority, -t.total_weight, sorted(t.areas)[0]))

        # Re-index trip IDs sequentially 1..N
        for idx, t in enumerate(trips, start=1):
            t.trip_id = idx

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return RoutePlan(
            algorithm_name=self.name,
            trips=trips,
            unassigned=unassignable,
            execution_time_ms=elapsed_ms
        )
