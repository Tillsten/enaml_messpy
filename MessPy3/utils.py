from scipy.constants import c

# Unit conversions

def THz2nm(nu):
    return cm2nm(THz2cm(nu))

def nm2THz(nm):
    return cm2THz(nm2cm(nm))

def cm2nm(cm):
    return 1e7/cm

def nm2cm(nm):
    return 1e7/nm

def THz2cm(nu):
    return (nu * 1e10) / c

def cm2THz(cm):
    return c / (cm * 1e10)

import numba as nb

@nb.jit
def inline_stats(arr):
    asum = 0
    asquared = 0
    amin = arr[0]
    amax = arr[0]

    for i in arr:
        asum += i
        asquared += i*i
        if i > amax:
            amax = i
        elif i < amin:
            amin = i

    mean = asum/arr.size
    std = (asquared - asum*asum/arr.size)/arr.size
    return asum, mean, std, amin, amax

