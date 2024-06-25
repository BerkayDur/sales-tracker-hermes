'''This file contains pytest configurations'''

from datetime import datetime

import pytest
import pandas as pd

@pytest.fixture(name='fake_products')
def fixture_fake_products():
    '''Contains some fake product reading data.'''
    return [
    {
        'product_id' : 1,
        'url' : 'https://www.asos.com/nike-running/nike-running-juniper\
-trail-2-gtx-trainers-in-grey/prd/205300355#colourWayId-205300357',
        'current_price' : 83.99,
        'price' : 104.99,
        'is_on_sale' : True,
        'reading_at' : datetime(2024,6,19,17,28,0),
        'product_name' : 'Nike Running Juniper Trail 2 GTX Trainers in Grey'
    },
    {
        'product_id' : 2,
        'url' : 'https://www.asos.com/nike-training/nike-training-everyday\
-lightweight-6-pack-no-show-socks-in-black/prd/205607655#colourWayId-205607656',
        'current_price' : 340.99,
        'price' : 350.99,
        'is_on_sale' : True,
        'reading_at' : datetime(2024,6,19,17,28,0),
        'product_name' : 'Nike training everyday lightweight 6 pack no show socks in black'
    },
    {
        'product_id' : 3,
        'url' : 'https://www.asos.com/nike-training/nike-training-everyday\
-lightweight-6-pack-no-show-socks-in-black/prd/205607655#colourWayId-205607656',
        'current_price' : 18.99,
        'price' : 19.99,
        'is_on_sale' : False,
        'reading_at' : datetime(2024,6,19,17,28,0),
        'product_name' : 'Falcon'
    }
]

@pytest.fixture(name='fake_merged_data')
def fixture_fake_merged_data():
    '''Contains some fake merged data.'''
    return pd.DataFrame([
        {'price_threshold': None, 'current_price': 18.99,
         'price': None, 'is_on_sale': False},
        {'price_threshold': None, 'current_price': 18.98,
         'price': 19.99, 'is_on_sale': False},
        {'price_threshold': None, 'current_price': 18.97,
         'price': None, 'is_on_sale': True},
        {'price_threshold': None, 'current_price': 18.96,
         'price': 19.98, 'is_on_sale': True},
        {'price_threshold': 16.99, 'current_price': 18.95,
         'price': None, 'is_on_sale': False},
        {'price_threshold': 16.98, 'current_price': 18.94,
         'price': 19.99, 'is_on_sale': False},
        {'price_threshold': 16.97, 'current_price': 18.93,
         'price': None, 'is_on_sale': True},
        {'price_threshold': 16.96, 'current_price': 18.92,
         'price': 19.99, 'is_on_sale': True},
        {'price_threshold': 19.99, 'current_price': 18.91,
         'price': None, 'is_on_sale': False},
        {'price_threshold': 19.98, 'current_price': 18.90,
         'price': None, 'is_on_sale': True},
        {'price_threshold': 19.97, 'current_price': 18.89,
         'price': 19.97, 'is_on_sale': False},
        {'price_threshold': 19.96, 'current_price': 18.88,
         'price': 20.99, 'is_on_sale': True},
        {'price_threshold': 19.95, 'current_price': 18.87,
         'price': 20.98, 'is_on_sale': False},
    ])
