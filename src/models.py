"""
Data models and validation for the Delivery Route Planner.
"""

from dataclasses import dataclass, field
from typing import List, Set, Tuple, Optional
import math


def normalize_area(area: str) -> str:
    """Canonicalizes area names (e.g. 'maadi', 'mAADI', '  Maadi  ' -> 'Maadi')."""
    if not area:
        return ""
    cleaned = " ".join(str(area).strip().split())
    canon_map = {
        "maadi": "Maadi",
        "nasr city": "Nasr City",
        "zamalek": "Zamalek",
        "heliopolis": "Heliopolis",
        "dokki": "Dokki",
        "new cairo": "New Cairo",
        "6th of october": "6th of October"
    }
    return canon_map.get(cleaned.lower(), cleaned.title())


@dataclass
class Delivery:
    """Represents a single package delivery request."""
    id: int
    area: str
    priority: int
    weight: float

    def __post_init__(self):
        # Enforce clean data types
        self.id = int(self.id)
        self.area = normalize_area(self.area)
        self.priority = int(self.priority)
        try:
            val = float(self.weight)
            self.weight = round(val, 3) if not math.isnan(val) else float('nan')
        except (ValueError, TypeError):
            self.weight = float('nan')

    def is_overweight(self, max_capacity: float = 10.0) -> bool:
        """Returns True if the package exceeds the vehicle's capacity threshold."""
        if math.isnan(self.weight):
            return False
        return self.weight > max_capacity + 1e-6

    def is_valid(self) -> Tuple[bool, Optional[str]]:
        """Validates delivery fields."""
        if math.isnan(self.weight):
            return False, "Package weight is NaN (Not a Number) or missing"
        if self.weight <= 0:
            return False, f"Package weight must be positive, got {self.weight} kg"
        if self.priority <= 0:
            return False, f"Priority must be a positive integer (>= 1), got {self.priority}"
        if not self.area:
            return False, "Delivery area must not be empty"
        return True, None


@dataclass
class Trip:
    """Represents a single delivery vehicle trip with a hard 10.0 kg limit."""
    trip_id: int
    deliveries: List[Delivery] = field(default_factory=list)

    @property
    def total_weight(self) -> float:
        """Sum of all package weights in this trip rounded to 2 decimal places."""
        return round(sum(d.weight for d in self.deliveries), 2)

    @property
    def remaining_capacity(self) -> float:
        """Remaining capacity in kg up to the 10.0 kg threshold."""
        return max(0.0, round(10.0 - self.total_weight, 2))

    @property
    def areas(self) -> Set[str]:
        """Set of distinct areas visited during this trip."""
        return {d.area for d in self.deliveries}

    @property
    def min_priority(self) -> int:
        """The highest urgency tier in this trip (lowest number = highest priority)."""
        if not self.deliveries:
            return 999999
        return min(d.priority for d in self.deliveries)

    def can_fit(self, delivery: Delivery, max_capacity: float = 10.0) -> bool:
        """Check whether a delivery can fit within vehicle capacity constraint."""
        return round(self.total_weight + delivery.weight, 4) <= (max_capacity + 1e-6)

    def add_delivery(self, delivery: Delivery) -> bool:
        """Safely add delivery if within capacity limit."""
        if not self.can_fit(delivery):
            return False
        self.deliveries.append(delivery)
        return True

    def remove_delivery(self, delivery_id: int) -> Optional[Delivery]:
        """Remove delivery by ID, returns the removed delivery if found."""
        for i, d in enumerate(self.deliveries):
            if d.id == delivery_id:
                return self.deliveries.pop(i)
        return None


@dataclass
class RoutePlan:
    """Represents the complete routing solution for a set of deliveries."""
    algorithm_name: str
    trips: List[Trip] = field(default_factory=list)
    unassigned: List[Tuple[Delivery, str]] = field(default_factory=list)
    execution_time_ms: float = 0.0

    @property
    def total_deliveries_assigned(self) -> int:
        return sum(len(t.deliveries) for t in self.trips)

    @property
    def total_weight_delivered(self) -> float:
        return round(sum(t.total_weight for t in self.trips), 2)

    @property
    def average_utilization_pct(self) -> float:
        """Percentage of total vehicle capacity utilized across all trips."""
        if not self.trips:
            return 0.0
        total_capacity = len(self.trips) * 10.0
        return round((self.total_weight_delivered / total_capacity) * 100.0, 1)

    @property
    def single_area_trip_ratio(self) -> float:
        """Ratio of trips that visit strictly 1 single area (1.0 = perfect spatial clustering)."""
        if not self.trips:
            return 1.0
        pure_trips = sum(1 for t in self.trips if len(t.areas) == 1)
        return round(pure_trips / len(self.trips), 2)
