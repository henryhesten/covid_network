from dataclasses import dataclass, field
from typing import Optional

from covid_network.distributionContinuous import DistributionContinuous, marcov_binary, DistributionConstCont
from covid_network.event import Event


@dataclass
class Person:
    id: str
    base_day_rate: DistributionContinuous
    starting_infected_prb: float = 0
    single_events: list[Event] = field(default_factory = lambda: [])
    interactions: list = field(default_factory = lambda: [])
    symptomatic: Optional[bool] = None
    infected_by: Optional[str] = None
    contagious_from_inc: Optional[int] = None
    contagious_to_inc: Optional[int] = None
    days_to_contagious: Optional[int] = None  # relative to infection day
    contagious_duration: Optional[int] = None  # in days
    _infected_on: Optional[int] = None
    symptoms_start: Optional[int] = None
    trustworthy_prb: float = 1
    _is_trustworthy: Optional[bool] = None  # do they warn people when they have symptoms
    _knows_they_might_have_been_infected_on_day: Optional[int] = None  # even if they no longer have symptoms
    
    def was_infected(self) -> bool:
        return self._infected_on is not None
    
    def is_infected_on_day(self, day: int) -> bool:
        if self._infected_on is None:
            return False
        return self._infected_on <= day
    
    def get_events_after_marcov(self, day: int) -> list[Event]:
        return [e for e in self.single_events if e.day.sample() == day and e.did_occur_after_marcov()]
    
    def get_interactions_after_marcov(self, day: int) -> list:
        return [i for i in self.interactions if i.day.sample() == day and i.did_occur_after_marcov()]
    
    # I.e. contagious and no symptoms, or know they may have it and is not trustworthy
    def practically_contagious(self, day: int) -> bool:
        if not self.was_infected():
            return False
        if self.contagious_from_inc > day or self.contagious_to_inc < day:
            return False
        if self.knows_they_might_have_been_infected(day) and self.is_trustworthy():
            return False
        return True
    
    def knows_they_might_have_been_infected(self, day: int) -> bool:
        if self._knows_they_might_have_been_infected_on_day is not None and day >= self._knows_they_might_have_been_infected_on_day:
            return True
        return self.symptomatic and day > self.symptoms_start
    
    def is_trustworthy(self) -> bool:
        if self._is_trustworthy is None:
            self._is_trustworthy = marcov_binary(self.trustworthy_prb)
        return self._is_trustworthy
    
    def warn_potential_infection_on(self, day: int) -> None:
        if self._knows_they_might_have_been_infected_on_day is not None \
                and self._knows_they_might_have_been_infected_on_day <= day:
            return
        
        self._knows_they_might_have_been_infected_on_day = day
        for inter in self.interactions:
            if inter.day.sample() >= day:
                inter.warn_participants_of_infection()


def unique_people(people: list[Person]) -> bool:
    ids = [p.id for p in people]
    return len(ids) == len(set(ids))


def describe_people(people: list[Person]):
    out_str = ""
    for person in people:
        if person.was_infected():
            desc = person.infected_by.split(";")[0]
            symp = "sympt" if person.symptomatic else "Asympt"
            out_str += f"{person.id} {desc} {symp}.  "
        else:
            out_str += f"{person.id} no-infection.  "
    return out_str
