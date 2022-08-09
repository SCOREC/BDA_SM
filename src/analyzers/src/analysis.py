from typing import Dict, Iterable
import numpy as np
import scipy.stats
from scipy.integrate import simps
from analyzers.src.request_manager import SamplerRequestManager

def stats(sampler_manager: SamplerRequestManager, data: Iterable, samples: int):
    ys = sampler_manager.get_sample(data, samples)
    mean = np.mean(ys, axis=0)
    std = np.std(ys, axis=0)
    return mean, std

def sample(sampler_manager: SamplerRequestManager, data: Iterable, samples: int):
    return sampler_manager.get_sample(data, samples)

def get_cov_means(ys):
    return np.cov(ys.T), np.mean(ys, axis=0)

def integrator(sampler_manager: SamplerRequestManager, data: Iterable, samples: int, function_table: np.array):
    ys = sampler_manager.get_sample(data, samples)
    cov, means = get_cov_means(ys)
    rv = scipy.stats.multivariate_normal(means, cov)
    # multiply function table by rv.pdf        
    return simps(final_ys, list(function_table.keys()))

def matplotlib():
    pass

