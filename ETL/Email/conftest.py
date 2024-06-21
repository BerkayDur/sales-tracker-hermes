'''This file contains pytest configurations'''

from datetime import datetime

import pytest

@pytest.fixture(name='fake_products')
def fixture_fake_products():
    '''Contains some fake product reading data.'''
    return [
    {
        'product_id' : 1,
        'url' : 'https://www.asos.com/nike-running/nike-running-juniper\
-trail-2-gtx-trainers-in-grey/prd/205300355#colourWayId-205300357',
        'current_price' : 83.99,
        'previous_price' : 104.99,
        'is_on_sale' : True,
        'reading_at' : datetime(2024,6,19,17,28,0),
        'product_name' : 'Nike Running Juniper Trail 2 GTX Trainers in Grey'
    },
    {
        'product_id' : 2,
        'url' : 'https://www.asos.com/nike-training/nike-training-everyday\
-lightweight-6-pack-no-show-socks-in-black/prd/205607655#colourWayId-205607656',
        'current_price' : 340.99,
        'previous_price' : 350.99,
        'is_on_sale' : True,
        'reading_at' : datetime(2024,6,19,17,28,0),
        'product_name' : 'Nike training everyday lightweight 6 pack no show socks in black'
    },
    {
        'product_id' : 3,
        'url' : 'https://www.asos.com/nike-training/nike-training-everyday\
-lightweight-6-pack-no-show-socks-in-black/prd/205607655#colourWayId-205607656',
        'current_price' : 18.99,
        'previous_price' : 19.99,
        'is_on_sale' : False,
        'reading_at' : datetime(2024,6,19,17,28,0),
        'product_name' : 'Falcon'
    }
]
