from typing import Dict, Iterable
import numpy as np
import scipy.stats
from scipy.integrate import simps
import matplotlib.pyplot as plt
from analyzers.src.request_manager import SamplerRequestManager

def stats(sampler_manager: SamplerRequestManager, data: Iterable, samples: int):
    ys = sampler_manager.get_sample(data, samples)
    mean = np.mean(ys, axis=1)
    std = np.std(ys, axis=1)
    return mean, std

def sample(sampler_manager: SamplerRequestManager, data: Iterable, samples: int):
    return sampler_manager.get_sample(data, samples)

# i assumed 1-d x so see if this works for 2-d
def integrator(sampler_manager: SamplerRequestManager, data: Iterable, samples: int, function_table: Dict[float, float]):
    mean, std = stats(sampler_manager, data, samples)
    pdf_values = scipy.stats.norm(mean, std).pdf(list(function_table.keys()))
    final_ys = np.multiply(list(function_table.values()), pdf_values)
    return simps(final_ys, list(function_table.keys()))

def matplotlib():
    pass

