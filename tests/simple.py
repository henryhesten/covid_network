import copy
import sys
import time
import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np
import IPython

from covid_network.config import Config
from covid_network.distributionContinuous import DistributionBeta
from covid_network.distributionDiscrete import DistributionDiscrete, const_distribution
from covid_network.event import Event
from covid_network.infector import Infector
from covid_network.interaction import Interaction
from covid_network.person import Person, describe_people

#%%
'''
#%%
%matplotlib qt
mpl.rcParams.update({"font.size":18, 'figure.figsize':[12,9]})
#%%
'''

#%%
config = Config()


def single_interation():
    harold: Person = Person("harold", DistributionBeta(True, 0.9, 1e-6))
    sophie: Person = Person("sophie", DistributionBeta(True, 0.001, 0.005))
    
    SHOPPING_INC = 3
    for d in range(100):
        event = Event(
                DistributionDiscrete(True, np.arange(SHOPPING_INC) + d * SHOPPING_INC, [1 / SHOPPING_INC] * SHOPPING_INC),
                0,
                f"shopping {d}",
                config = config
        )
        harold.single_events.append(event)
    
    for d in range(300):
        Interaction(day = const_distribution(d),
                    prob_infection = 0.5,
                    description = f"sophie-harold {d}",
                    probability_occurring = 0.2,
                    people = [harold, sophie],
                    config = config)
    
    people = [harold, sophie]
    
    infector: Infector = Infector(config, people)
    infector.propagate(100)
    
    return sophie, harold


#%%
t0 = time.time()
outputs = []
for i in range(100):
    out = single_interation()
    outputs.append(out)
    print(i, out[0]._infected_on, out[1]._infected_on)
t1 = time.time()
print(t1 - t0)

#%%

plt.clf()
for i in [0, 1]:
    h_inf = [h[i]._infected_on if h[i]._infected_on is not None else 101 for h in outputs]
    values, base = np.histogram(h_inf, bins = 40)
    cumulative = np.cumsum(values)
    cumulative = cumulative / cumulative[-1]
    plt.plot(base[:-1], cumulative)
