"tests for individual citation templates. not all of them are ready yet"

# import requests
# import time

from warnings import warn

import requests
import pytest

from citeurl import Citator
from .test_templates import TESTS

@pytest.mark.parametrize('template', TESTS.keys())
def test_link(template):
    test_data = TESTS[template]
    if not test_data.get('URL'):
        warn(f'SKIPPED {template} - no URL')
        return
    print(f'{template} ({test_data["URL"]}) ... ', end='')
    try:
        response = requests.get(test_data['URL'])
    except requests.exceptions.SSLError:
        warn(f'SKIPPED {template} - SSL error')
        return
    if response.status_code == 403:
        warn(f'SKIPPED {template} - Error 403 (Forbidden)')
        return
    assert response.ok, f"{test_data['URL']} returned {response.status_code}"

