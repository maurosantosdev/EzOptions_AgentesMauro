import pandas as pd
from scipy.stats import norm
from math import log, sqrt
from datetime import datetime

# Funções de cálculo de greeks, independentes de Streamlit e de outros arquivos.

def calculate_greeks(flag, S, K, t, sigma, r):
    """Calcula delta, gamma e vanna para uma opção."""
    try:
        t = max(t, 1/525600) # Mínimo de 1 minuto em anos
        d1 = (log(S / K) + (r + 0.5 * sigma**2) * t) / (sigma * sqrt(t))
        d2 = d1 - sigma * sqrt(t)
        
        if flag == 'c':
            delta_val = norm.cdf(d1)
        else: # put
            delta_val = norm.cdf(d1) - 1
        
        gamma_val = norm.pdf(d1) / (S * sigma * sqrt(t))
        vanna_val = -norm.pdf(d1) * d2 / sigma
        
        return delta_val, gamma_val, vanna_val
    except (ValueError, ZeroDivisionError):
        return 0, 0, 0 # Return 0 instead of None for failed calculations

def calculate_charm(flag, S, K, t, sigma, r):
    """Calcula o charm (dDelta/dTime) para uma opção."""
    try:
        t = max(t, 1/525600)
        d1 = (log(S / K) + (r + 0.5 * sigma**2) * t) / (sigma * sqrt(t))
        d2 = d1 - sigma * sqrt(t)
        norm_d1 = norm.pdf(d1)
        
        if flag == 'c':
            charm = -norm_d1 * (2*r*t - d2*sigma*sqrt(t)) / (2*t*sigma*sqrt(t))
        else: # put
            charm = -norm_d1 * (2*r*t - d2*sigma*sqrt(t)) / (2*t*sigma*sqrt(t)) - r*norm.cdf(-d2)
        
        return charm
    except (ValueError, ZeroDivisionError):
        return 0 # Return 0 instead of None for failed calculations

def compute_and_process_greeks(calls, puts, S, expiry_date_str, risk_free_rate):
    """Função centralizada que recebe dataframes e calcula os greeks."""
    if calls.empty or puts.empty:
        return pd.DataFrame(), pd.DataFrame() # Return empty DataFrames

    selected_expiry = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
    today = datetime.today().date()
    t_days = (selected_expiry - today).days

    if t_days < 0:
        print(f"Data de expiração no passado: {expiry_date_str}")
        return pd.DataFrame(), pd.DataFrame() # Return empty DataFrames

    t = t_days / 365.0
    r = risk_free_rate

    def process_df(df, flag):
        df = df.copy()
        
        # Ensure all expected Greek columns exist before processing
        # Initialize with 0 to avoid KeyError if no valid rows exist later
        for col in ['calc_delta', 'calc_gamma', 'VEX', 'calc_charm', 'GEX', 'DEX', 'Charm']:
            if col not in df.columns:
                df[col] = 0.0

        if df.empty:
            return df

        # Drop rows where impliedVolatility is missing or invalid, as it's crucial for Greeks
        df = df.dropna(subset=['impliedVolatility'])
        df = df[df['impliedVolatility'] > 0]
        df = df.drop_duplicates(subset=['strike'])
        df = df.reset_index(drop=True)

        if df.empty:
            return df

        # Calculate greeks
        greeks_results = df.apply(
            lambda row: calculate_greeks(flag, S, row["strike"], t, row["impliedVolatility"], r),
            axis=1, result_type='expand'
        )
        greeks_results.columns = ['calc_delta', 'calc_gamma', 'VEX'] # VEX is the raw vanna value

        # Calculate charm
        charm_results = df.apply(
            lambda row: calculate_charm(flag, S, row["strike"], t, row["impliedVolatility"], r),
            axis=1
        )
        charm_results.name = 'calc_charm'

        # Combine greeks and charm into the DataFrame
        df['calc_delta'] = greeks_results['calc_delta']
        df['calc_gamma'] = greeks_results['calc_gamma']
        df['VEX'] = greeks_results['VEX']
        df['calc_charm'] = charm_results

        # Fill any remaining NaN values in Greek columns with 0 (from failed calculations)
        for col in ['calc_delta', 'calc_gamma', 'VEX', 'calc_charm']:
            df[col] = df[col].fillna(0)
        
        # Debugging: Print sum of Charm to check if values are non-zero
        print(f"Debug: Sum of Charm for {flag} options: {df['Charm'].sum()}")

        # Calculate exposures
        df["GEX"] = df["calc_gamma"] * df["openInterest"] * 100 * S * S * 0.01
        df["DEX"] = df["calc_delta"] * df["openInterest"] * 100 * S
        df["VEX"] = df["VEX"] * df["openInterest"] * 100 * S # VEX is now the exposure
        df["Charm"] = df["calc_charm"] * df["openInterest"] * 100 * S / 365.0
        
        return df

    processed_calls = process_df(calls, 'c')
    processed_puts = process_df(puts, 'p')

    return processed_calls, processed_puts
