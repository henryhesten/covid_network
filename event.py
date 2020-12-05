from dataclasses import dataclass
from typing import Optional

from covid_network.abstractEvent import AbstractEvent
from covid_network.distributionContinuous import marcov_binary
from covid_network.distributionDiscrete import DistributionDiscrete


@dataclass
class Event(AbstractEvent):
    infection_occurred: Optional[bool] = None
    
    def did_infection_after_marcov(self) -> bool:
        if self.infection_occurred is None:
            prb_infection = self.prob_infection
            prb_infection *= self.config.rate_pessimism_factor
            self.infection_occurred = marcov_binary(self.prob_infection)
        
        return self.infection_occurred
