import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
import matplotlib as mpl

#  https://science.sciencemag.org/content/sci/368/6491/eabb6936.full.pdf

#%%
'''
#%%
%matplotlib qt
mpl.rcParams.update({"font.size":18, 'figure.figsize':[12,9]})
#%%
'''
#%%
xx = np.linspace(0, 20, 1000)

sig = 0.5
mu = 1.63
yy = scipy.stats.lognorm.pdf(xx, sig, 0, np.exp(mu))
plt.clf()
plt.plot(xx, yy)
plt.plot(xx, np.cumsum(yy) / sum(yy))

zz = scipy.stats.lognorm.cdf(xx, sig, 0, np.exp(mu))
plt.plot(xx, zz, '*')

pred_mean = np.exp(mu + sig**2 / 2)
act_mean = sum(xx * yy) / sum(yy)
print(act_mean, pred_mean)

uu = np.linspace(0, 1, 1000)
ww = scipy.stats.lognorm.ppf(uu, sig, 0, np.exp(mu))
plt.plot(ww, uu, "--")
