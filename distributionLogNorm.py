from dataclasses import dataclass

import scipy.stats
import numpy as np

from covid_network.distribution import Distribution


@dataclass
class DistributionLogNormRounded(Distribution):
    mu: float  # NOT THE MEAN
    sig: float
    
    def _sample(self) -> float:
        rnd_float = np.random.random()
        not_rounded = scipy.stats.lognorm.ppf(rnd_float, self.sig, 0, np.exp(self.mu))
        return np.round(not_rounded)
