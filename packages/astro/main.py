#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage
from resolvers import JsonRestResolver

NEO_LOOKUP_BASE = 'https://api.nasa.gov/neo/rest/v1/neo'

class Package(GnrDboPackage):
    
    def config_attributes(self):
        return dict(comment='astro package',sqlschema='astro',
                    name_short='Astro', name_long='Astro', name_full='Astro')

    def config_db(self, pkg):
        pass
    
class Table(GnrDboTable):
    
    def get_api_key(self):
        return self.db.application.config['nasa?api_key'] or 'DEMO_KEY'
    
    def fetch_history(self, asteroid_id=None, neo_ref=None, **kwargs): 
        resolver = JsonRestResolver(
            f'{NEO_LOOKUP_BASE}/{neo_ref}',
            cacheTime=3600,
            api_key=self.get_api_key())
        data = resolver()
        return data