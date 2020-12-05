from dataclasses import dataclass, field
from typing import Optional

from covid_network.abstractEvent import AbstractEvent
from covid_network.config import Config
from covid_network.distributionContinuous import marcov_binary
from covid_network.person import Person, unique_people


@dataclass
class Interaction(AbstractEvent):
    people: list[Person] = None
    __person_infected: list[Optional[bool]] = field(default_factory = lambda: None, init = False)
    __a_infected_b: list[list[Optional[bool]]] = field(default_factory = lambda: None, init = False)
    
    def __post_init__(self):
        assert unique_people(self.people)
        self.__a_infected_b = []
        for pa in self.people:
            tmp = []
            for pb in self.people:
                tmp.append(None)
            self.__a_infected_b.append(tmp)
        
        self.__person_infected = []
        for p in self.people:
            self.__person_infected.append(None)
        
        for p in self.people:
            p.interactions.append(self)
    
    def __get_ind(self, person: Person) -> int:
        return [p.id for p in self.people].index(person.id)
    
    def a_infected_b_after_marcov(self, pa: Person, pb: Person) -> bool:
        inda = self.__get_ind(pa)
        indb = self.__get_ind(pb)
        if self.__a_infected_b[inda][indb] is None:
            self.__a_infected_b[inda][indb] = self.__a_infected_b_after_marcov(pa, pb)
        
        return self.__a_infected_b[inda][indb]
    
    def __a_infected_b_after_marcov(self, pa: Person, pb: Person) -> bool:
        if pa.id == pb.id:
            return False
        if pa.practically_contagious(self.day.sample()):
            prb_infection = self.prob_infection
            prb_infection *= self.config.rate_pessimism_factor
            if not pa.symptomatic:
                prb_infection *= self.config.asymptomatic_infectious_factor
            if prb_infection > 1:
                prb_infection = 1
            return marcov_binary(prb_infection)
        return False
    
    def was_person_infected_after_marcov(self, person: Person) -> bool:
        ind = self.__get_ind(person)
        if self.__person_infected[ind] is None:
            infected = False
            for maybe_infected_by in self.people:
                infected = infected or self.a_infected_b_after_marcov(maybe_infected_by, person)
            self.__person_infected[ind] = infected
        return self.__person_infected[ind]
    
    def warn_participants_of_infection(self) -> None:
        for person in self.people:
            person.warn_potential_infection_on(self.day.sample())
