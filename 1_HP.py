import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import statsmodels.api as sm
import pandas_datareader as pdr
import numpy as np

# set the start and end dates for the data
start_date = '1955-01-01'
end_date = '2022-01-01'

# download the data from FRED using pandas_datareader
gdp = web.DataReader('RGDPNAQAA666NRUG', 'fred', start_date, end_date)
log_gdp = np.log(gdp)

# apply a Hodrick-Prescott filter to the data to extract the cyclical component
cycle, trend1600 = sm.tsa.filters.hpfilter(log_gdp, lamb=1600)
cycle, trend100 = sm.tsa.filters.hpfilter(log_gdp, lamb=100)
cycle, trend10 = sm.tsa.filters.hpfilter(log_gdp, lamb=10)

# Plot the original time series data
plt.plot(log_gdp, label="Original GDP (in log)")

# Plot the trend component
plt.plot(trend1600, label="$\lambda$=1600")
plt.plot(trend100, label="$\lambda$=100")
plt.plot(trend10, label="$\lambda$=10")


plt.legend()
plt.title('Qatar')
# Add a legend and show the plot
plt.legend()
plt.savefig('gdp_trend_qatar.pdf')
plt.show()