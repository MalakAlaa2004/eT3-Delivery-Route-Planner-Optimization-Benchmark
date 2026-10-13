"""
Abstract base solver interface for delivery route optimization.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
from src.models import Delivery, RoutePlan


class BaseSolver(ABC):
    """Abstract interface for all delivery routing algorithms."""

    def __init__(self, name: str, max_capacity: float = 10.0):
        self.name = name
        self.max_capacity = max_capacity

    def filter_and_validate(self, deliveries: List[Delivery]) -> Tuple[List[Delivery], List[Tuple[Delivery, str]]]:
        """
        Validates deliveries and separates valid requests from unassignable ones
        (e.g., packages exceeding max vehicle capacity of 10.0 kg, or invalid weights).
        """
        valid: List[Delivery] = []
        unassignable: List[Tuple[Delivery, str]] = []
        seen_ids = set()

        for d in deliveries:
            is_valid, err = d.is_valid()
            if not is_valid:
                unassignable.append((d, f"Invalid delivery data: {err}"))
            elif d.id in seen_ids:
                unassignable.append((d, f"Duplicate delivery ID #{d.id} detected - cleaned and skipped to preserve unique trip integrity"))
            elif d.is_overweight(self.max_capacity):
                unassignable.append((d, f"Weight ({d.weight} kg) exceeds maximum vehicle capacity ({self.max_capacity} kg)"))
            else:
                seen_ids.add(d.id)
                valid.append(d)

        return valid, unassignable

    @abstractmethod
    def solve(self, deliveries: List[Delivery]) -> RoutePlan:
        """Solves the delivery route planning problem and returns a RoutePlan."""
        pass
