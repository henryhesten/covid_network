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
DOCTOR_SCALING = 11  # https://www.thelancet.com/journals/lanpub/article/PIIS2468-2667(20)30164-X/fulltext

BASE_RATE_DAILY_GOV = 15000 / 66e6
GOV_UNDERESTIMATE = 3.02
BASE_RATE_DAILY = BASE_RATE_DAILY_GOV * GOV_UNDERESTIMATE

# /10 seams reasonable, also matches going to the shop each day
# https://www.microcovid.org/?distance=normal&duration=20&interaction=oneTime&personCount=5&riskProfile=average&setting=indoor&subLocation=United_Kingdom_England&theirMask=basic
# &topLocation=United_Kingdom&voice=silent&yourMask=basic
SENSIBLE_RATE = BASE_RATE_DAILY / 10
DOC_RATE = DOCTOR_SCALING * BASE_RATE_DAILY

config: Config = Config()


def single_sim(h_see_r = 30, h_see_s = 39):
    stephani: Person = Person("stephani", DistributionBeta(True, 1e-12, 1e-16))
    henry: Person = Person("henry", DistributionBeta(True, SENSIBLE_RATE, SENSIBLE_RATE / 2))
    rach: Person = Person("rach", DistributionBeta(True, SENSIBLE_RATE, SENSIBLE_RATE / 2))
    jess: Person = Person("jess", DistributionBeta(True, SENSIBLE_RATE, SENSIBLE_RATE / 2))
    kath: Person = Person("kath", DistributionBeta(True, DOC_RATE, DOC_RATE / 2))
    
    # Before Rach BDay
    for d in range(h_see_r):
        Interaction(day = const_distribution(d),
                    prob_infection = HOUSEHOLD_RATE,
                    description = f"flat;{d}",
                    probability_occurring = 1,
                    people = [rach, jess, kath],
                    config = config)
    
    # On Rach BDAY
    Interaction(day = const_distribution(h_see_r),
                prob_infection = HOUSEHOLD_RATE,
                description = f"flat;{h_see_r}",
                probability_occurring = 1,
                people = [rach, jess, kath, henry],
                config = config)
    Interaction(day = const_distribution(h_see_r),
                prob_infection = SEX_RATE,
                description = f"sex-h-r",
                probability_occurring = 1,
                people = [rach, henry],
                config = config)
    
    # Henry see Stephani
    Interaction(day = const_distribution(h_see_s),
                prob_infection = SEX_RATE,
                description = f"sex-h-s",
                probability_occurring = 1,
                people = [stephani, henry],
                config = config)
    
    people = [stephani, henry, rach, jess, kath]
    
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
kath_base_prb = 0.1
h_see_r = 50
h_see_s = 56
num_sims = 10**5
for i in range(num_sims):
    out = single_sim(h_see_s = h_see_s, h_see_r = h_see_r)
    print(100 * i / num_sims, [x._infected_on for x in out])
    outputs.append(out)

print(f"Reasonable rates")
print(f"h_see_r = {h_see_r}")
print(f"h_see_s = {h_see_s}")
no_symptoms_reported = [x for x in outputs if not reported_symptoms_before(x, h_see_s)]
print(f"Finished {len(outputs)}, {len(no_symptoms_reported)} reported no symptoms")

stephani_infected = [x for x in no_symptoms_reported if x[0].was_infected()]
s_risk = len(stephani_infected) / len(no_symptoms_reported)
print(f"Of these cases, Stephani infected {len(stephani_infected)} times: {100 * s_risk}%")

stephani_infected_check = [x for x in outputs if x[0].was_infected()]
assert len(stephani_infected) == len(stephani_infected)

#%%
descs = [describe_people(out) for out in outputs]
uniq_c(descs)
