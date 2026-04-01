"""Test script for JsonRestResolver against Open Notify API.

Open Notify API endpoints (no auth required):
  - http://api.open-notify.org/iss-now.json  — current ISS position
  - http://api.open-notify.org/astros.json   — people currently in space

Run:
    cd /Users/developer/sviluppo/genropy_projects/astro/packages/astro/lib
    PYTHONPATH=/Users/developer/sviluppo/genropy/gnrpy python3 test_resolver.py
"""

from resolvers import JsonRestResolver


def test_iss_position():
    print('=== ISS Current Position ===')
    resolver = JsonRestResolver('http://api.open-notify.org/iss-now.json', cacheTime=30)
    result = resolver()

    assert result['message'] == 'success', f"Expected 'success', got {result['message']}"

    lat = result['iss_position.latitude']
    lon = result['iss_position.longitude']
    print(f'  Latitude:  {lat}')
    print(f'  Longitude: {lon}')
    print(f'  Timestamp: {result["timestamp"]}')

    # Verify cache: second call should return same timestamp
    result2 = resolver()
    assert result['timestamp'] == result2['timestamp'], 'Cache not working!'
    print('  Cache: OK (same timestamp on second call)')
    print()


def test_astronauts():
    print('=== People in Space ===')
    resolver = JsonRestResolver('http://api.open-notify.org/astros.json', cacheTime=60)
    result = resolver()

    assert result['message'] == 'success', f"Expected 'success', got {result['message']}"

    count = result['number']
    print(f'  Total: {count} people')
    print()

    people = result['people']
    for key in people.keys():
        person = people[key]
        print(f'  - {person["name"]:30s} ({person["craft"]})')
    print()


def test_error_handling():
    print('=== Error Handling ===')
    resolver = JsonRestResolver('http://api.open-notify.org/nonexistent', timeout=5)
    result = resolver()

    assert 'error' in result.keys(), 'Expected error key in result'
    print(f'  Error caught: {result["error"][:80]}...')
    print()


def test_bag_with_resolvers():
    from gnr.core.gnrbag import Bag

    print('=== Bag with Resolvers ===')
    bag = Bag()
    bag['iss'] = JsonRestResolver('http://api.open-notify.org/iss-now.json', cacheTime=30)
    bag['astronauts'] = JsonRestResolver('http://api.open-notify.org/astros.json', cacheTime=60)

    print('  ISS Position:')
    pos = bag['iss']
    print(f'    Lat: {pos["iss_position.latitude"]}, Lon: {pos["iss_position.longitude"]}')

    print('  Astronauts:')
    astros = bag['astronauts']
    for key in astros['people'].keys():
        person = astros['people'][key]
        print(f'    - {person["name"]} ({person["craft"]})')
    print()


if __name__ == '__main__':
    test_iss_position()
    test_astronauts()
    test_error_handling()
    test_bag_with_resolvers()
    print('All tests passed!')
