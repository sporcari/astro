# -*- coding: utf-8 -*-

from datetime import datetime, timezone
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
from resolvers import JsonRestResolver

NEO_LOOKUP_BASE = 'https://api.nasa.gov/neo/rest/v1/neo'


class GnrCustomWebPage(object):
    py_requires = """public:Public,th/th:TableHandler"""

    def main(self, root, **kwargs):
        bc = root.borderContainer(datapath='main', padding='10px')

        top = bc.contentPane(region='top', height='100px')
        fb = top.formlet(datapath='.parameters', cols=3)
        fb.dbselect(value='^.asteroid_id', table='astro.asteroid',
                    auxColumns='$neo_reference_id,$approach_count',
                    hasDownArrow=True,
                    lbl='Asteroid', validate_notnull=True, width='25em')
        fb.dataRpc(self.fetch_history,
            asteroid_id='^.asteroid_id',
            _lockScreen=True)

        center = bc.contentPane(region='center', margin='2px')
        center.plainTableHandler(
            table='astro.asteroid_approach',
            condition='$asteroid_id=:aid',
            condition_aid='^.parameters.asteroid_id',
            viewResource='ViewFromAsteroid',
            height='100%')

   