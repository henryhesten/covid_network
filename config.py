from dataclasses import dataclass, field

import numpy as np

from covid_network.distribution import Distribution
from covid_network.distributionContinuous import DistributionContinuous, DistributionBeta
from covid_network.distributionDiscrete import DistributionDiscrete
from covid_network.distributionLogNorm import DistributionLogNormRounded


@dataclass
class Config:
    symptomatic_prb_mean: float = 0.575  #https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7281624/
    symptomatic_prb_sd: float = 0.2
    symptomatic_global: bool = True
    _symptomatic_prb: DistributionContinuous = None
    
    asymptomatic_infectious_factor: float = 0.1  # https://science.sciencemag.org/content/sci/368/6491/eabb6936.full.pdf
    
    rate_pessimism_factor: float = 1  # multiplies all infection rates
    duration_pessimism_factor: float = 1  # multiplies contagiousness duration
    
    _contagious_offset_rel_symptoms_smpt: DistributionDiscrete = None
    _contagious_offset_rel_symptoms_asmpt: DistributionDiscrete = None
    
    _contagious_duration_sym: DistributionDiscrete = None
    _days_to_symptoms: Distribution = None
    
    #_contagious_duration_asym: DistributionDiscrete = None
    
    _contagious_duration_array: np.array = np.array([7, 9, 11, 13, 15])
    
    def __post_init__(self):
        self._contagious_duration_array = np.floor(self._contagious_duration_array * self.duration_pessimism_factor)
    
    def symptomatic_dist(self):
        if self._symptomatic_prb is None:
            self._symptomatic_prb = DistributionBeta(
                    self.symptomatic_global, self.symptomatic_prb_mean, self.symptomatic_prb_sd)
        return self._symptomatic_prb
    
    def contagious_offset_rel_symptoms(self, symptomatic: bool):
        return self.contagious_offset_rel_symptoms_smpt() if symptomatic else self.contagious_offset_rel_symptoms_asym()
    
    # https://www.medrxiv.org/content/medrxiv/early/2020/06/11/2020.05.08.20094870.full.pdf
    def contagious_offset_rel_symptoms_smpt(self):
        if self._contagious_offset_rel_symptoms_smpt is None:
            self._contagious_offset_rel_symptoms_smpt = DistributionDiscrete(False, list(np.arange(-6, 6)), [1 / 12.] * 12)
        return self._contagious_offset_rel_symptoms_smpt
    
    def contagious_offset_rel_symptoms_asym(self):
        return self.contagious_offset_rel_symptoms_smpt()
    
    def contagious_duration_dist(self, symptomatic: bool):
        return self.contagious_duration_sym_dist() if symptomatic else self.contagious_duration_asym_dist()
    
    # https://academic.oup.com/cid/advance-article/doi/10.1093/cid/ciaa886/5864499
    def contagious_duration_sym_dist(self):
        if self._contagious_duration_sym is None:
            self._contagious_duration_sym = DistributionDiscrete(False, self._contagious_duration_array, [1 / 5.] * 5)
        return self._contagious_duration_sym
    
    def contagious_duration_asym_dist(self):
        return self.contagious_duration_sym_dist()
    
    #  https://science.sciencemag.org/content/sci/368/6491/eabb6936.full.pdf
    def days_to_symptoms_dist(self):
        if self._days_to_symptoms is None:
            self._days_to_symptoms = DistributionLogNormRounded(False, 1.63, 0.5)  # Note that these parameters are NOT the mean and sd
        return self._days_to_symptoms
