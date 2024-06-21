'''Helpers to assist in the dashboard'''

import re


WEBSITES = ('asos',)

class MatchingError(Exception):
    '''Exception regarding matching a pattern.'''

def extract_website_name(url: str) -> str:
    '''Given a url extract the website name.'''
    if not isinstance(url, str):
        raise TypeError('url must be a string.')

    try:
        return re.findall(r'(?<=www\.).+(?=\.co)', url)[0]
    except IndexError as e:
        raise MatchingError("Cannot determine website name from url.") from e


if __name__ == '__main__':
    print(extract_website_name('''https://www.asos.com/nike/nike-air-force-1-07-\
trainers-in-triple-white/prd/202389207#colourWayId-202389212'''))
