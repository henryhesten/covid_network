from dataclasses import dataclass

import numpy as np

from covid_network.distribution import Distribution


@dataclass
class DistributionDiscrete(Distribution):
    outcomes: list[object]
    probabilities: list[float]
    
    def __post_init__(self):
        if np.abs(1 - sum(self.probabilities)) > 1e-4:
            raise Exception(f"Probabilities do not sum to 1: {self.probabilities}")
    
    def _sample(self) -> float:
        return np.random.choice(self.outcomes, p = self.probabilities)


def const_distribution(value):
    return DistributionDiscrete(True, [value], [1])
