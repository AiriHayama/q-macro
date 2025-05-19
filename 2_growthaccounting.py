import pandas as pd
import numpy as np

# pwt90 = pd.read_stata('https://www.rug.nl/ggdc/docs/pwt90.dta')
pwt63 = pd.read_excel('/Users/airihayama/keio-macro/q-macro/pwt63_w_country_names.xls')

oecd_countries = [
    'Japan', 'United States',
]

# data = pwt90[
#     pwt90['country'].isin(oecd_countries) &
#     pwt90['year'].between(1960, 2000)
# ]
data = pwt63[
    pwt63['country'].isin(oecd_countries) &
    pwt63['year'].between(1960, 2000)
]

# relevant_cols = ['countrycode', 'country', 'year', 'rgdpna', 'rkna', 'pop', 'emp', 'avh', 'labsh', 'rtfpna']
relevant_cols = ['isocode', 'country', 'year', 'POP', 'rgdpwok', 'rgdpl', 'rgdptt', 'ki', 'kg']
data = data[relevant_cols].dropna()

data['Y'] = data['rgdpl'] * data['POP'] * 1000
data['K'] = data['ki'] * 0.01 * data['Y']
# data['y'] = data['rgdpwok']
# data['y'] = (1.0 - data['kg'] * 0.01) * data['rgdpl']
data['y_n'] = data['rgdpl']
# data['y'] = (1.0 - data['kg'] * 0.01) * data['rgdpwok']
data['k'] = data['ki'] * data['rgdpl'] * 0.01
# data['alpha'] = data['rgdptt'] * data['ki'] * 0.01 / data['y_n']
data['alpha'] = data['rgdptt'] * data['K'] / data['Y']
data['A'] = data['y_n'] / (data['k'] ** data['alpha'])
data = data.sort_values('year').groupby('isocode').apply(lambda x: x.assign(
    y_shifted=100 * x['y_n'] / x['y_n'].iloc[0],
    k_shifted=100 * x['k'] / x['k'].iloc[0],
    alpha_shifted=100 * x['alpha'] / x['alpha'].iloc[0],
    A_shifted=100 * x['A'] / x['A'].iloc[0],
)).reset_index(drop=True).dropna()


def calculate_growth_rates(country_data):
    
    start_year_actual = country_data['year'].min()
    end_year_actual = country_data['year'].max()

    start_data = country_data[country_data['year'] == start_year_actual].iloc[0]
    end_data = country_data[country_data['year'] == end_year_actual].iloc[0]

    years = end_data['year'] - start_data['year']

    g_y = ((end_data['y_n'] / start_data['y_n']) ** (1/years) - 1) * 100

    g_k = ((end_data['k'] / start_data['k']) ** (1/years) - 1) * 100

    g_a = ((end_data['A'] / start_data['A']) ** (1/years) - 1) * 100

    alpha_avg = (start_data['alpha'] + end_data['alpha']) / 2.0
    capital_deepening_contrib = alpha_avg * g_k
    tfp_growth_calculated = g_a
    
    tfp_share = (tfp_growth_calculated / g_y)
    cap_share = (capital_deepening_contrib / g_y)

    return {
        'Country': start_data['country'],
        'Growth Rate': round(g_y, 2),
        'TFP Growth': round(tfp_growth_calculated, 2),
        'Capital Deepening': round(capital_deepening_contrib, 2),
        'TFP Share': round(tfp_share, 2),
        'Capital Share': round(cap_share, 2)
    }


results_list = data.groupby('country').apply(calculate_growth_rates).dropna().tolist()
results_df = pd.DataFrame(results_list)

avg_row_data = {
    'Country': 'Average',
    'Growth Rate': round(results_df['Growth Rate'].mean(), 2),
    'TFP Growth': round(results_df['TFP Growth'].mean(), 2),
    'Capital Deepening': round(results_df['Capital Deepening'].mean(), 2),
    'TFP Share': round(results_df['TFP Share'].mean(), 2),
    'Capital Share': round(results_df['Capital Share'].mean(), 2)
}
results_df = pd.concat([results_df, pd.DataFrame([avg_row_data])], ignore_index=True)

print("\nGrowth Accounting in OECD Countries: 1960-2000 period")
print("="*85)
print(results_df.to_string(index=False))

""""
Growth Accounting in OECD Countries: 1960-2000 period Aghion Howitt2009
=====================================================================================
      Country  Growth Rate  TFP Growth  Capital Deepening  TFP Share  Capital Share
        Japan         3.28        2.73               0.56       0.83           0.17
United States         1.89        1.09               0.80       0.58           0.42

Growth Accounting in OECD Countries: 1960-2000 period
=====================================================================================
      Country  Growth Rate  TFP Growth  Capital Deepening  TFP Share  Capital Share
        Japan         4.21        1.26               1.01       0.30           0.24
United States         1.82        1.40              -0.05       0.77          -0.03
      Average         3.02        1.33               0.48       0.54           0.10

Growth Accounting in OECD Countries: 1960-2000 period y
=====================================================================================
      Country  Growth Rate  TFP Growth  Capital Deepening  TFP Share  Capital Share
        Japan         3.94        3.76               0.17       0.96           0.04
United States         1.83        1.54               0.28       0.84           0.16
      Average         2.88        2.65               0.23       0.90           0.10      
"""