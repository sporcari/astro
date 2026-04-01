"""JsonRestResolver - BagResolver subclass for JSON REST API calls.

A reusable resolver that performs HTTP GET requests to REST APIs,
parses JSON responses, and returns Bag structures. Designed for
Open Notify and NASA API integrations.

Usage in RPC methods:
    from gnr.core.gnrbag import Bag
    from resolvers import JsonRestResolver

    resolver = JsonRestResolver('http://api.open-notify.org/iss-now.json',
                                cacheTime=30)
    result = resolver()  # returns Bag with parsed JSON

Usage with query parameters:
    resolver = JsonRestResolver('https://api.nasa.gov/planetary/apod',
                                cacheTime=300,
                                headers={'Accept': 'application/json'},
                                api_key='DEMO_KEY', date='2024-01-01')
    result = resolver()
"""

import requests
from gnr.core.gnrbag import Bag, BagResolver


class JsonRestResolver(BagResolver):
    """BagResolver that fetches JSON from a REST API via HTTP GET.

    Positional args (classArgs):
        url: The endpoint URL.

    Keyword args (classKwargs):
        cacheTime: Cache TTL in seconds. 0=no cache, <0=infinite. Default 0.
        readOnly: If True, value not stored in node. Default True.
        timeout: Request timeout in seconds. Default 30.
        headers: Dict of HTTP headers. Default None.

    Any extra kwargs are sent as query string parameters.
    """

    classKwargs = {
        'cacheTime': 0,
        'readOnly': True,
        'timeout': 30,
        'headers': None,
    }
    classArgs = ['url']

    def load(self):
        """Fetch the URL, parse JSON, return a Bag."""
        params = {k: v for k, v in self.kwargs.items() if v is not None}
        headers = self.headers or {}
        headers.setdefault('Accept', 'application/json')
        try:
            response = requests.get(self.url, params=params,
                                    headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            result = Bag()
            result.setItem('error', str(e), status='error')
            return result

        data = response.json()
        result = Bag()
        result.fromJson(data)
        return result

