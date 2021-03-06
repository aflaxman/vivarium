import pytest

import random

import pandas as pd
import numpy as np

from vivarium.interpolation import Interpolation

def test_1d_interpolation():
    df = pd.DataFrame({'a': np.arange(100), 'b': np.arange(100), 'c': np.arange(100, 0, -1)})
    df = df.sample(frac=1) # Shuffle table to assure interpolation works given unsorted input

    i = Interpolation(df, (), ('a',))

    query = pd.DataFrame({'a': np.arange(100, step=0.01)})

    assert np.allclose(query.a, i(query).b)
    assert np.allclose(100-query.a, i(query).c)

def test_age_year_interpolation():
    years = list(range(1990,2010))
    ages = list(range(0,90))
    pops = np.array(ages)*11.1
    data = []
    for age, pop in zip(ages, pops):
        for year in years:
            for sex in ['Male', 'Female']:
                data.append({'age':age, 'sex':sex, 'year':year, 'pop':pop})
    df = pd.DataFrame(data)
    df = df.sample(frac=1) # Shuffle table to assure interpolation works given unsorted input

    i = Interpolation(df, ('sex', 'age'), ('year',))

    assert np.allclose(i(year=[1990,1990], age=[35,35], sex=['Male', 'Female']), 388.5)

def test_2d_interpolation():
    a = np.mgrid[0:5,0:5][0].reshape(25)
    b = np.mgrid[0:5,0:5][1].reshape(25)
    df = pd.DataFrame({'a': a, 'b': b, 'c': b, 'd': a})
    df = df.sample(frac=1) # Shuffle table to assure interpolation works given unsorted input

    i = Interpolation(df, (), ('a', 'b'))

    query = pd.DataFrame({'a': np.arange(4, step=0.01), 'b': np.arange(4, step=0.01)})

    assert np.allclose(query.b, i(query).c)
    assert np.allclose(query.a, i(query).d)

def test_interpolation_with_categorical_parameters():
    a = ['one']*100 + ['two']*100
    b = np.append(np.arange(100), np.arange(100))
    c = np.append(np.arange(100), np.arange(100, 0, -1))
    df = pd.DataFrame({'a': a, 'b': b, 'c': c})
    df = df.sample(frac=1) # Shuffle table to assure interpolation works given unsorted input

    i = Interpolation(df, ('a',), ('b',))

    query_one = pd.DataFrame({'a': 'one', 'b': np.arange(100, step=0.01)})
    query_two = pd.DataFrame({'a': 'two', 'b': np.arange(100, step=0.01)})

    assert np.allclose(np.arange(100, step=0.01), i(query_one))

    assert np.allclose(np.arange(100, 0, step=-0.01), i(query_two))

def test_interpolation_with_function():
    df = pd.DataFrame({'a': np.arange(100), 'b': np.arange(100), 'c': np.arange(100, 0, -1)})
    df = df.sample(frac=1) # Shuffle table to assure interpolation works given unsorted input

    i = Interpolation(df, (), ('a',), func=lambda x: x * 2)

    query = pd.DataFrame({'a': np.arange(100, step=0.01)})

    assert np.allclose(query.a * 2, i(query).b)

def test_order_zero_2d():
    a = np.mgrid[0:5,0:5][0].reshape(25)
    b = np.mgrid[0:5,0:5][1].reshape(25)
    df = pd.DataFrame({'a': a + 0.5, 'b': b + 0.5, 'c': b*3, 'garbage': ['test']*len(a)})
    df = df.sample(frac=1) # Shuffle table to assure interpolation works given unsorted input

    i = Interpolation(df, ('garbage',), ('a', 'b'), order=0)

    column = np.arange(4, step=0.011)
    query = pd.DataFrame({'a': column, 'b': column, 'garbage': ['test']*(len(column))})

    assert np.allclose(query.b.astype(int) * 3, i(query))
