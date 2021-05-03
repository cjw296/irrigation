import numpy as np
import pandas as pd

π = np.pi


def saturation_vapour_pressure(t):
    return 0.6108 * np.exp((17.27*t)/(t+237.3))


def evapotranspiration(daily, latitude: float, altitude: float, α: float = 0.23):
    # 0.23 is hypothetical grass reference crop
    Tmax = daily['Tx_0909']
    Tmin = daily['Tn_0909']
    Tmean = daily['Tmean_909'] = (Tmax + Tmin) / 2
    Rs = daily['srad_0024']
    u2 = daily['U2run_0909'] * 1_000 / (24 * 60 * 60)  # Original unit is km / day
    Δ = 4098 * saturation_vapour_pressure(Tmean) / ((Tmean + 237.3) ** 2)
    Pmean = (daily['P_max'] + daily['P_min']) / 2
    γ = 0.000665 * Pmean
    DT = Δ / (Δ + γ * (1 + 0.34 * u2))
    PT = γ / (Δ + γ * (1 + 0.34 * u2))
    TT = (900 / (Tmean + 273)) * u2
    es = (saturation_vapour_pressure(Tmax) + saturation_vapour_pressure(Tmin)) / 2
    ea = (saturation_vapour_pressure(Tmin) * daily['RH_max'] /
          100 + saturation_vapour_pressure(Tmax) * daily['RH_min'] / 100) / 2
    J = pd.Series(daily.index.shift(-1, freq='D').day_of_year, index=daily.index)
    dr = 1 + 0.033 * np.cos((2 * π / 365) * J)
    δ = 0.409 * np.sin((2 * π / 365) * J - 1.39)
    φ = latitude * π / 180
    ωs = np.arccos(-np.tan(φ) * np.tan(δ))
    Gsc = 0.0820
    Ra = (24*60/π)*Gsc*dr*((ωs*np.sin(φ)*np.sin(δ)) + (np.cos(φ)*np.cos(δ)*np.sin(ωs)))
    Rso = (0.75 + altitude * 2e-5) * Ra
    Rns = (1 - α) * Rs
    σ = 4.903e-9
    Rnl = σ*(((Tmax+273.16)**4 + (Tmin+273.16)**4)/2)*(0.34-0.14*np.sqrt(ea))*(1.35*Rs/Rso - 0.35)
    Rn = Rns - Rnl
    Rng = 0.408 * Rn
    ETrad = DT * Rng
    ETwind = PT * TT * (es - ea)
    return ETwind + ETrad
