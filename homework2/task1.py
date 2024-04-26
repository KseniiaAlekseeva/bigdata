from functools import reduce

import pandas as pd


def mapper(ind):
    n = 1
    score = df['price'][ind]
    return score, score ** 2, n


def reducer(score_data1, score_data2):
    s1, s12, n1 = score_data1
    s2, s22, n2 = score_data2
    return s1 + s2, s12 + s22, n1 + n2


df = pd.read_csv('../../AB_NYC_2019.csv')
print(f'Mean value: {df['price'].mean()}.')
print(f'Variance: {df['price'].var()}.')

mx, mx2, num = reduce(reducer, map(mapper, list(df.index)))
mean = mx / num
disp = (mx2 / num - (mx / num) ** 2)

print(f'Mean value: {mean}.')
print(f'Variance: {disp}.')
