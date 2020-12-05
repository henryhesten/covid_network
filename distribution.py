from abc import abstractmethod, ABC
from dataclasses import dataclass, InitVar, field


@dataclass
class Distribution(ABC):
    cache_output: bool  # whether distribution should be sampled once and cached or sampled repeatedly
    __cached_value: float = field(default = None, init = False)
    
    @abstractmethod
    def _sample(self):
        pass
    
    def sample(self):
        if not self.cache_output:
            return self._sample()
        
        if self.__cached_value is None:
            self.__cached_value = self._sample()
        return self.__cached_value
