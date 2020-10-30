import numpy as np
import matplotlib.pyplot as plt
import h5py as h5
from fwd_PV.tools.fft import Fourier_ks
from fwd_PV.tools.cosmo import camb_PS
from fwd_PV.io import process_config
from math import pi
import sys

configfile = sys.argv[1]

N_BOX, L, _, _, _,\
        datafile, savedir, _, _= process_config(configfile)

l = L / N_BOX
V = L**3

kh, pk = camb_PS()

_, k_abs = Fourier_ks(N_BOX, l)

k_bins = np.logspace(np.log10(2 * pi / L), np.log10(2*pi * N_BOX / L), 41)
k_bincentre = np.sqrt(k_bins[1:]*k_bins[:-1])

J = np.complex(0., 1.)

def measure_Pk(delta_k, k_norm, k_bins):
    Pk_sample = []
    for i in range(len(k_bins)-1):
        select_k = (k_norm > k_bins[i])&(k_norm < k_bins[i+1])
        if(np.sum(select_k) < 1):
            Pk_sample.append(0.)
        else:
            Pk_sample.append(np.mean(delta_k[0,select_k]**2 + delta_k[1,select_k]**2) * V)
    return np.array(Pk_sample)

Pk_measured_list = []
ln_prob_list = []

N_START = int(sys.argv[2])
N_END = int(sys.argv[3])

for i in range(N_START, N_END):
    print("Reading mcmc_"+str(i)+".h5")
    f = h5.File(savedir + '/mcmc_'+str(i)+'.h5', 'r')
    delta_k = f['delta_k'][:]
    ln_prob = f['ln_prob'].value
    ln_prob_list.append(ln_prob)
    if(i>N_START):
        Pk_sample = measure_Pk(delta_k, k_abs, k_bins)
        Pk_measured_list.append(Pk_sample)
Pk_measured = np.array(Pk_measured_list)

plt.plot(np.arange(N_START, N_END), np.array(ln_prob_list))
plt.savefig(savedir+'/figs/ln_prob.png', dpi=150)
plt.close()
# np.save(savedir+'/Pk_measured.npy', Pk_measured)
# np.save(savedir+'/k_bins.npy', k_bins)

Pk_measured_mean = np.mean(Pk_measured, axis=0)
Pk_measured_low  = np.percentile(Pk_measured, 16., axis=0)
Pk_measured_high = np.percentile(Pk_measured, 84., axis=0)

plt.ylim(3.0e+2, 4.0e+4)
plt.xlim(1.e-2, 1.)
plt.loglog(k_bincentre, Pk_measured_mean, color='b')
plt.fill_between(k_bincentre, Pk_measured_low, Pk_measured_high, color='b', alpha=0.3)
#plt.axhline(1000., color='k')
plt.loglog(kh, pk, 'k', label='CAMB')
plt.legend()
plt.savefig(savedir+'/figs/Pk_samples.png', dpi=150)
plt.close()

print("Pk_measured.shape: "+str(Pk_measured.shape))
