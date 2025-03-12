import numpy as np
import pandas as pd
from scipy.stats import norm


def calculate_var(data,stock,period, confidence_level=0.99, num_simulations=100000):
    data['Returns'] = data['close'].pct_change().dropna()
    
    
    returns = data['Returns'].dropna()*100
    mean_return = returns.mean()
    std_dev = returns.std()
    z_score = norm.ppf(1 - confidence_level)
    
    # 1. Historical VaR (Non-Parametric)
    var_historical = np.percentile(returns, (1 - confidence_level) * 100)
    
    # 2. Parametric VaR (Variance-Covariance)
    var_parametric = mean_return + z_score * std_dev
    
    # 3. Monte Carlo VaR (Simulating future price movements)
    simulated_returns = np.random.normal(mean_return, std_dev, num_simulations)
    var_monte_carlo = np.percentile(simulated_returns, (1 - confidence_level) * 100)
    
    # 4. Conditional VaR (Expected Shortfall, more conservative risk measure)
    cvar_historical = returns[returns <= var_historical].mean()
    cvar_parametric = mean_return + (z_score / (1 - confidence_level)) * std_dev
    cvar_monte_carlo = simulated_returns[simulated_returns <= var_monte_carlo].mean()
    
    # 5. Hybrid VaR (Weighted Average for Robustness)
    var_hybrid = (var_historical + var_parametric + var_monte_carlo) / 3
    cvar_hybrid = (cvar_historical + cvar_parametric + cvar_monte_carlo) / 3
    
    return {
        "Stock": stock,
        "Period": period,
        "Confidence_Level": confidence_level,
        "Historical_VaR": round(var_historical, 2),
        "Parametric_VaR": round(var_parametric, 2),
        "Monte_Carlo_VaR": round(var_monte_carlo, 2),
        "Conditional_Historical_VaR": round(cvar_historical, 2),
        "Conditional_Parametric_VaR": round(cvar_parametric, 2),
        "Conditional_Monte_Carlo_VaR": round(cvar_monte_carlo, 2),
        "Hybrid_VaR": round(var_hybrid, 2),
        "Hybrid_Conditional_VaR": round(cvar_hybrid, 2)
    }

