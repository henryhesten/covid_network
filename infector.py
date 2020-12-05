import time

from covid_network.config import Config
from covid_network.distributionContinuous import DistributionContinuous, marcov_binary
from covid_network.distributionDiscrete import DistributionDiscrete
from covid_network.person import Person
import numpy as np


class Infector:
    def __init__(self, config: Config, people: list[Person], day: int = 0):
        self.people: dict[str, Person] = {p.id: p for p in people}
        self.day: int = day
        self.config: Config = config
    
    def start_and_propagate(self, num_days) -> None:
        for person in self.people.values():
            if marcov_binary(person.starting_infected_prb):
                self.infect(person, 0, "started-infected")
        self.propagate(num_days)
    
    def propagate(self, num_days) -> None:
        for d in range(num_days):
            self.step_day()
    
    def step_day(self) -> None:
        for person in self.people.values():
            infected, cause = self.maybe_infect_person(person)
            if infected:
                self.infect(person, self.day, cause)
        self.day += 1
    
    def maybe_infect_person(self, person: Person) -> tuple[bool, str]:
        if person.is_infected_on_day(self.day):
            return False, "already infected"
        
        if marcov_binary(person.base_day_rate.sample()):
            return True, "base:0"
        
        for evt in person.get_events_after_marcov(self.day):
            if evt.did_infection_after_marcov():
                return True, f"event:{evt.description}"
        
        for inter in person.get_interactions_after_marcov(self.day):
            if inter.was_person_infected_after_marcov(person):
                return True, f"interaction:{inter.description}"
        
        return False, "not infected"
    
    def infect(self, person: Person, day: int, cause: str) -> None:
        person.infected_by = cause
        person.infected_on = day
        person.symptomatic = marcov_binary(self.config.symptomatic_dist().sample())
        
        symptoms_start = person.infected_on + self.config.days_to_symptoms_dist().sample()  # no symptoms is asymptomatic, but still used later
        contagious_offset = self.config.contagious_offset_rel_symptoms(person.symptomatic).sample()
        contagious_start = symptoms_start + contagious_offset
        if contagious_start <= day:
            contagious_start = day + 1
        
        person.contagious_from_inc = contagious_start
        person.contagious_duration = self.config.contagious_duration_dist(person.symptomatic).sample()
        person.contagious_to_inc = person.contagious_from_inc + person.contagious_duration - 1
        
        if person.symptomatic:
            person.symptoms_start = symptoms_start
            person.warn_potential_infection_on(person.symptoms_start - self.config.warn_interactions_days_before_symptoms, person.symptoms_start)
