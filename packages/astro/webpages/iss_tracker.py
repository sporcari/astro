# -*- coding: utf-8 -*-

from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
from resolvers import JsonRestResolver


class GnrCustomWebPage(object):

    def main(self, root, **kwargs):
        bc = root.borderContainer(datapath='iss_tracker')
        bc.dataRpc('.position', self.get_iss_position,
                   _timing=10, _onStart=True)
        top = bc.contentPane(region='top', height='120px',
                             padding='10px')
        top.div('ISS Tracker', font_size='1.5em', font_weight='bold',
                margin_bottom='10px')
        fb = top.formbuilder(cols=2, border_spacing='4px', fld_width='12em')
        fb.textbox(value='^.position.latitude', lbl='Latitudine',
                   readOnly=True)
        fb.textbox(value='^.position.longitude', lbl='Longitudine',
                   readOnly=True)

    @public_method
    def get_iss_position(self, **kwargs):
        """Fetch current ISS position from Open Notify API."""
        resolver = JsonRestResolver('http://api.open-notify.org/iss-now.json',
                                    cacheTime=10)
        data = resolver()
        if 'error' in data.keys():
            return data
        result = Bag()
        result['latitude'] = float(data['iss_position.latitude'])
        result['longitude'] = float(data['iss_position.longitude'])
        result['timestamp'] = data['timestamp']
        return result

    @public_method
    def get_astronauts(self, **kwargs):
        """Fetch list of people currently in space from Open Notify API."""
        resolver = JsonRestResolver('http://api.open-notify.org/astros.json',
                                    cacheTime=60)
        data = resolver()
        if 'error' in data.keys():
            return data
        result = Bag()
        result['number'] = data['number']
        people = Bag()
        for i, key in enumerate(data['people'].keys()):
            person = data['people'][key]
            people.setItem(f'r_{i}', None,
                           name=person['name'],
                           craft=person['craft'])
        result['people'] = people
        return result
