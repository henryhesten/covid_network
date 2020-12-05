from common.common_functions import uniq_c
from covid_network.config import Config
from covid_network.distributionContinuous import DistributionBeta
from covid_network.distributionDiscrete import const_distribution
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
HOUSEHOLD_RATE = 0.25
SEX_RATE = 1

config: Config = Config()


def single_sim(katie_base_prb = 0.1, h_see_r = 30, h_see_s = 39):
    sophie: Person = Person("sophie", DistributionBeta(True, 1e-12, 1e-16))
    harold: Person = Person("harold", DistributionBeta(True, 1e-12, 1e-16))
    rose: Person = Person("rose", DistributionBeta(True, 1e-12, 1e-16))
    charlie: Person = Person("charlie", DistributionBeta(True, 1e-12, 1e-16))
    katie: Person = Person("katie", DistributionBeta(True, katie_base_prb, 1e-16))
    
    # Before rose BDay
    for d in range(h_see_r):
        Interaction(day = const_distribution(d),
                    prob_infection = HOUSEHOLD_RATE,
                    description = f"flat;{d}",
                    probability_occurring = 1,
                    people = [rose, charlie, katie],
                    config = config)
    
    # On rose BDAY
    Interaction(day = const_distribution(h_see_r),
                prob_infection = HOUSEHOLD_RATE,
                description = f"flat;{h_see_r}",
                probability_occurring = 1,
                people = [rose, charlie, katie, harold],
                config = config)
    Interaction(day = const_distribution(h_see_r),
                prob_infection = SEX_RATE,
                description = f"sex-h-r",
                probability_occurring = 1,
                people = [rose, harold],
                config = config)
    
    # harold see sophie
    Interaction(day = const_distribution(h_see_s),
                prob_infection = SEX_RATE,
                description = f"sex-h-s",
                probability_occurring = 1,
                people = [sophie, harold],
                config = config)
    
    people = [sophie, harold, rose, charlie, katie]
    
    infector: Infector = Infector(config, people)
    infector.propagate(h_see_s + 1)
    
    return people


def reported_symptoms_before(people, day):
    for person in people:
        if person.knows_they_might_have_been_infected(day):
            return True
    return False


#%%
outputs = []
katie_base_prb = 0.1
h_see_r = 30
h_see_s = 36
num_sims = 10**6
for i in range(num_sims):
    out = single_sim(katie_base_prb = katie_base_prb, h_see_s = h_see_s, h_see_r = h_see_r)
    print(100 * i / num_sims, [x._infected_on for x in out])
    outputs.append(out)

print(f"katie_base_prb = {katie_base_prb}")
print(f"h_see_r = {h_see_r}")
print(f"h_see_s = {h_see_s}")
no_symptoms_reported = [x for x in outputs if not reported_symptoms_before(x, h_see_s)]
print(f"Finished {len(outputs)}, {len(no_symptoms_reported)} reported no symptoms")

sophie_infected = [x for x in no_symptoms_reported if x[0].was_infected()]
s_risk = len(sophie_infected) / len(no_symptoms_reported)
print(f"Of these cases, sophie infected {len(sophie_infected)} times: {100 * s_risk}%")

sophie_infected_check = [x for x in outputs if x[0].was_infected()]
assert len(sophie_infected) == len(sophie_infected)

#%%
descs = [describe_people(out) for out in outputs]
uniq_c(descs)

#%%
for out in outputs:
    sophie = out[0]
    if sophie.was_infected():
        break
