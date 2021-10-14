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

