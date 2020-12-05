from abc import ABC
from dataclasses import dataclass

import numpy as np

from covid_network.distribution import Distribution


@dataclass
class DistributionContinuous(Distribution, ABC):
    pass


@dataclass
class DistributionConstCont(DistributionContinuous):
    value: float
    
    def _sample(self):
        return self.value


@dataclass
class DistributionBeta(DistributionContinuous):
    mean: float
    sd: float
    
    def _sample(self) -> float:
        a, b = self.get_alpha_beta()
        out = np.random.beta(a, b)
        return out
    
    def get_alpha_beta(self) -> tuple[float, float]:
        if self.sd**2 >= self.mean * (1 - self.mean):
            raise Exception(f"Mean and SD out of range for beta distribution, {self.mean}, {self.sd}")
        
        t1 = self.mean * (1 - self.mean) / self.sd**2 - 1
        return self.mean * t1, (1 - self.mean) * t1


def marcov_binary(prb) -> bool:
    return np.random.choice([True, False], p = [prb, 1 - prb])
