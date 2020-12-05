from abc import ABC
from dataclasses import dataclass, field
from typing import Optional

from covid_network.config import Config
from covid_network.distributionContinuous import marcov_binary
from covid_network.distributionDiscrete import DistributionDiscrete


@dataclass
class AbstractEvent(ABC):
    day: DistributionDiscrete = None
    prob_infection: float = -1  # from a *symptomatic* person, when using an interaction
    description: str = ""
    config: Config = None
    probability_occurring: float = 1
    __event_occurred: Optional[bool] = field(default = None, init = False)
    
    def did_occur_after_marcov(self) -> bool:
        if self.__event_occurred is None:
            self.__event_occurred = marcov_binary(self.probability_occurring)
        
        return self.__event_occurred
