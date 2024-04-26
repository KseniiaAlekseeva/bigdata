import pandas as pd

df=pd.read_csv('../../AB_NYC_2019.csv')
print(f'Mean value: {df['price'].mean()}.')
print(f'Variance: {df['price'].var()}.')

