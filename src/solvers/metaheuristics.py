"""
Metaheuristic optimization solvers:
1. Simulated Annealing (SA)
2. Genetic Algorithm (GA)
Provides multi-objective combinatorial optimization for delivery route planning.
"""

import time
import math
import random
from typing import List, Dict, Tuple
from collections import defaultdict
from src.models import Delivery, Trip, RoutePlan
from src.solvers.base import BaseSolver


def evaluate_cost(
    assignment: Dict[int, int],
    deliveries_by_id: Dict[int, Delivery],
    max_capacity: float = 10.0,
    weight_capacity_penalty: float = 10000.0,
    weight_trip_count: float = 80.0,
    weight_area_dispersion: float = 40.0,
    weight_priority_inversion: float = 30.0
) -> float:
    """
    Multi-objective cost function to minimize:
    Cost = Overweight Penalties + Trip Count Minimization + Area Dispersion + Priority Inversion
    """
    trip_buckets = defaultdict(list)
    for d_id, t_id in assignment.items():
        trip_buckets[t_id].append(deliveries_by_id[d_id])

    active_trips = list(trip_buckets.values())
    total_cost = len(active_trips) * weight_trip_count

    for trip_deliveries in active_trips:
        trip_weight = sum(d.weight for d in trip_deliveries)
        # Heavy penalty for exceeding 10.0 kg
        if trip_weight > max_capacity + 1e-6:
            excess = trip_weight - max_capacity
            total_cost += weight_capacity_penalty + (excess ** 2) * 5000.0

        # Spatial Cohesion penalty: trips with multiple distinct areas are penalized
        distinct_areas = {d.area for d in trip_deliveries}
        if len(distinct_areas) > 1:
            total_cost += (len(distinct_areas) - 1) * weight_area_dispersion

    # Priority Inversion penalty: sort trips by min_priority
    # If higher priority packages are scattered in later dispatches, penalize
    min_priorities = [min(d.priority for d in t) for t in active_trips]
    for i in range(len(min_priorities) - 1):
        if min_priorities[i] > min_priorities[i + 1]:
            total_cost += weight_priority_inversion

    return total_cost


def build_route_plan_from_assignment(
    assignment: Dict[int, int],
    deliveries_by_id: Dict[int, Delivery],
    algorithm_name: str,
    unassignable: List[Tuple[Delivery, str]],
    elapsed_ms: float
) -> RoutePlan:
    """Reconstructs a clean RoutePlan from a dictionary assignment."""
    trip_buckets = defaultdict(list)
    for d_id, t_id in assignment.items():
        trip_buckets[t_id].append(deliveries_by_id[d_id])

    trips: List[Trip] = []
    for raw_tid, trip_pkgs in trip_buckets.items():
        if trip_pkgs:
            trips.append(Trip(trip_id=raw_tid, deliveries=trip_pkgs))

    # Sort trips by urgency (lowest priority number first), then weight
    trips.sort(key=lambda t: (t.min_priority, -t.total_weight))

    for idx, t in enumerate(trips, start=1):
        t.trip_id = idx

    return RoutePlan(
        algorithm_name=algorithm_name,
        trips=trips,
        unassigned=unassignable,
        execution_time_ms=elapsed_ms
    )


class SimulatedAnnealingSolver(BaseSolver):
    """
    Simulated Annealing metaheuristic for Delivery Route Planning.
    Uses stochastic perturbation (reassignment & swaps) with Metropolis acceptance.
    """

    def __init__(
        self,
        name: str = "Simulated Annealing",
        max_capacity: float = 10.0,
        initial_temp: float = 100.0,
        cooling_rate: float = 0.95,
        min_temp: float = 0.1,
        iterations_per_temp: int = 40,
        seed: int = 42
    ):
        super().__init__(name=name, max_capacity=max_capacity)
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.iterations_per_temp = iterations_per_temp
        self.seed = seed

    def solve(self, deliveries: List[Delivery]) -> RoutePlan:
        start_time = time.perf_counter()
        random.seed(self.seed)

        valid_deliveries, unassignable = self.filter_and_validate(deliveries)
        if not valid_deliveries:
            return RoutePlan(
                algorithm_name=self.name,
                trips=[],
                unassigned=unassignable,
                execution_time_ms=(time.perf_counter() - start_time) * 1000.0
            )

        deliveries_by_id = {d.id: d for d in valid_deliveries}
        delivery_ids = [d.id for d in valid_deliveries]

        # Initial solution: simple grouping by area & priority
        current_assignment: Dict[int, int] = {}
        for idx, d in enumerate(valid_deliveries):
            current_assignment[d.id] = idx + 1  # Start one-per-trip, let SA consolidate

        # Quick greedy condensation for initial state
        temp_trips: List[Trip] = []
        for d in sorted(valid_deliveries, key=lambda x: (x.priority, x.area, -x.weight)):
            placed = False
            for t in temp_trips:
                if d.area in t.areas and t.can_fit(d, self.max_capacity):
                    t.add_delivery(d)
                    placed = True
                    break
            if not placed:
                temp_trips.append(Trip(trip_id=len(temp_trips) + 1, deliveries=[d]))

        for t in temp_trips:
            for d in t.deliveries:
                current_assignment[d.id] = t.trip_id

        current_cost = evaluate_cost(current_assignment, deliveries_by_id, self.max_capacity)
        best_assignment = dict(current_assignment)
        best_cost = current_cost

        temp = self.initial_temp

        while temp > self.min_temp:
            for _ in range(self.iterations_per_temp):
                candidate_assignment = dict(current_assignment)
                move_type = random.random()

                # Neighborhood Operator 1: Reassign single package
                if move_type < 0.6 or len(delivery_ids) < 2:
                    d_id = random.choice(delivery_ids)
                    current_trip = candidate_assignment[d_id]
                    # Target an existing trip or open a new one
                    existing_trips = list(set(candidate_assignment.values()))
                    new_trip_id = max(existing_trips) + 1
                    target_trip = random.choice(existing_trips + [new_trip_id])
                    if target_trip != current_trip:
                        candidate_assignment[d_id] = target_trip

                # Neighborhood Operator 2: Swap two packages
                else:
                    d1, d2 = random.sample(delivery_ids, 2)
                    candidate_assignment[d1], candidate_assignment[d2] = (
                        candidate_assignment[d2],
                        candidate_assignment[d1],
                    )

                candidate_cost = evaluate_cost(candidate_assignment, deliveries_by_id, self.max_capacity)
                delta_cost = candidate_cost - current_cost

                # Metropolis Acceptance Criterion
                if delta_cost < 0 or math.exp(-delta_cost / max(temp, 1e-5)) > random.random():
                    current_assignment = candidate_assignment
                    current_cost = candidate_cost

                    if current_cost < best_cost:
                        best_cost = current_cost
                        best_assignment = dict(candidate_assignment)

            temp *= self.cooling_rate

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return build_route_plan_from_assignment(
            best_assignment, deliveries_by_id, self.name, unassignable, elapsed_ms
        )


class GeneticAlgorithmSolver(BaseSolver):
    """
    Genetic Algorithm metaheuristic for Delivery Route Planning.
    Evolves a population of discrete chromosome allocations using tournament selection,
    two-point crossover, and mutation.
    """

    def __init__(
        self,
        name: str = "Genetic Algorithm",
        max_capacity: float = 10.0,
        population_size: int = 50,
        generations: int = 80,
        mutation_rate: float = 0.15,
        tournament_size: int = 3,
        seed: int = 42
    ):
        super().__init__(name=name, max_capacity=max_capacity)
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.seed = seed

    def solve(self, deliveries: List[Delivery]) -> RoutePlan:
        start_time = time.perf_counter()
        random.seed(self.seed)

        valid_deliveries, unassignable = self.filter_and_validate(deliveries)
        if not valid_deliveries:
            return RoutePlan(
                algorithm_name=self.name,
                trips=[],
                unassigned=unassignable,
                execution_time_ms=(time.perf_counter() - start_time) * 1000.0
            )

        n = len(valid_deliveries)
        deliveries_by_id = {d.id: d for d in valid_deliveries}
        delivery_ids = [d.id for d in valid_deliveries]

        # Upper bound for trip count
        max_trips = max(3, n)

        def chromosome_to_assignment(chrom: List[int]) -> Dict[int, int]:
            return {delivery_ids[i]: chrom[i] for i in range(n)}

        def calculate_fitness(chrom: List[int]) -> float:
            assignment = chromosome_to_assignment(chrom)
            cost = evaluate_cost(assignment, deliveries_by_id, self.max_capacity)
            return 1.0 / (1.0 + cost)

        # Initialize Population
        population: List[List[int]] = []
        for _ in range(self.population_size):
            chrom = [random.randint(1, max(2, n // 2 + 1)) for _ in range(n)]
            population.append(chrom)

        # Ensure one greedy-like seed individual in population
        seed_chrom = [0] * n
        t_id = 1
        acc_w = 0.0
        cur_area = None
        for i, d in enumerate(valid_deliveries):
            if cur_area is None:
                cur_area = d.area
            if d.area != cur_area or acc_w + d.weight > self.max_capacity:
                t_id += 1
                acc_w = 0.0
                cur_area = d.area
            seed_chrom[i] = t_id
            acc_w += d.weight
        population[0] = seed_chrom

        best_chrom = population[0]
        best_fitness = calculate_fitness(best_chrom)

        # Generations loop
        for _ in range(self.generations):
            fitness_scores = [calculate_fitness(ind) for ind in population]

            for i, fit in enumerate(fitness_scores):
                if fit > best_fitness:
                    best_fitness = fit
                    best_chrom = list(population[i])

            # Selection via Tournament
            def select_parent() -> List[int]:
                candidates = random.sample(range(self.population_size), self.tournament_size)
                best_idx = max(candidates, key=lambda idx: fitness_scores[idx])
                return population[best_idx]

            new_population: List[List[int]] = []
            # Elitism: Keep best individual
            new_population.append(list(best_chrom))

            while len(new_population) < self.population_size:
                p1 = select_parent()
                p2 = select_parent()

                # Crossover
                if n > 2 and random.random() < 0.8:
                    pt1, pt2 = sorted(random.sample(range(n), 2))
                    child = p1[:pt1] + p2[pt1:pt2] + p1[pt2:]
                else:
                    child = list(p1)

                # Mutation
                for gene_idx in range(n):
                    if random.random() < self.mutation_rate:
                        child[gene_idx] = random.randint(1, max_trips)

                new_population.append(child)

            population = new_population

        best_assignment = chromosome_to_assignment(best_chrom)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return build_route_plan_from_assignment(
            best_assignment, deliveries_by_id, self.name, unassignable, elapsed_ms
        )
