# -*- coding: utf-8 -*-

from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
from resolvers import JsonRestResolver


class GnrCustomWebPage(object):

    def main(self, root, **kwargs):
        bc = root.borderContainer(datapath='iss_tracker', padding='10px')
        bc.dataRpc('.position', self.get_iss_position,
                   _timing=10, _onStart=True)
        bc.dataRpc('.people', self.get_astronauts, _onStart=True)

        top = bc.contentPane(region='top')
        eb = top.expandbox(title='ISS Position', open=True, animate=True)
        fb = eb.formlet(datapath='.position')
        fb.textbox(value='^.latitude', lbl='Latitudine',
                   readOnly=True)
        fb.textbox(value='^.longitude', lbl='Longitudine',
                   readOnly=True)

        center = bc.contentPane(region='center')
        eb2 = center.expandbox(title='Astronauts', open=True, animate=True,
                               height='100%')
        grid = eb2.quickGrid(value='^.people', height='100%')
        grid.column(name='Name', field='name', width='20em')
        grid.column(name='Craft', field='craft', width='10em')

    @public_method
    def get_iss_position(self, **kwargs):
        """Fetch current ISS position from Open Notify API."""
        resolver = JsonRestResolver('http://api.open-notify.org/iss-now.json',
                                    cacheTime=10)
        data = resolver()
        return data['iss_position']

    @public_method
    def get_astronauts(self, **kwargs):
        """Fetch list of people currently in space from Open Notify API."""
        resolver = JsonRestResolver('http://api.open-notify.org/astros.json',
                                    cacheTime=60)
        data = resolver()
        return data['people']