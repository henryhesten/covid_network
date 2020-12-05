import numpy as np

from covid_network.config import Config
from covid_network.distributionContinuous import DistributionBeta
from covid_network.distributionDiscrete import const_distribution
from covid_network.infector import Infector
from covid_network.interaction import Interaction
from covid_network.person import Person

# https://www.medrxiv.org/content/10.1101/2020.05.23.20111559v2
# there is a 30% chance of catching covid from a flatmate

config = Config()


def single_sim(daily_flatmate_rate = 0.1, sim_days = 30):
    infected: Person = Person("infected", DistributionBeta(True, 1e-12, 1e-16), starting_infected_prb = 1)
    other: Person = Person("other", DistributionBeta(True, 1e-12, 1e-16))
    
    for d in range(sim_days):
        Interaction(day = const_distribution(d),
                    prob_infection = daily_flatmate_rate,
                    description = f"flat;{d}",
                    probability_occurring = 1,
                    people = [infected, other],
                    config = config)
    
    people = [other, infected]
    
    infector: Infector = Infector(config, people)
    infector.start_and_propagate(sim_days)
    return people


def mult_sims(daily_flatmate_rate = 0.1, sim_days = 30, sim_num = 100):
    other_infected_count = 0
    for i in range(sim_num):
        out = single_sim(daily_flatmate_rate, sim_days)
        if out[0].was_infected():
            other_infected_count += 1
    return other_infected_count / sim_num


#%%
#for days in [5, 8, 12, 16, 25, 50, 100, 300]:
#    print(days, mult_sims(0.25, days, 10000))

#%%
for rate in np.linspace(0.2, 0.3, 30):
    print(rate, mult_sims(rate, 50, 10000))
