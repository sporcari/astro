#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='astro package',sqlschema='astro',
                    name_short='Astro', name_long='Astro', name_full='Astro')

    def config_db(self, pkg):
        pass

    

class Table(GnrDboTable):
    
    def get_api_key(self):
        return self.db.application.config['nasa?api_key'] or 'DEMO_KEY'

