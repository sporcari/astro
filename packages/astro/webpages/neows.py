# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
from resolvers import JsonRestResolver

NEOWS_BASE = 'https://api.nasa.gov/neo/rest/v1'


class GnrCustomWebPage(object):

    def main(self, root, **kwargs):
        bc = root.borderContainer(datapath='main', padding='10px')

        top = bc.contentPane(region='top')
        eb = top.expandbox(title='Search Near Earth Objects', open=True,
                           animate=True)
        fb = eb.formlet(datapath='.parameters', cols=3)
        fb.dateTextBox(value='^.start_date', lbl='Start Date', width='12em',
                       period_to='.end_date')
        fb.dateTextBox(value='^.end_date', lbl='End Date', width='12em')
        fb.dataController("""if (start_date && end_date){
                          if ((end_date - start_date) > 7*86400000){
                              var new_end_date = new Date(start_date.getTime() + 7*86400000);
                              this.setRelativeData('.end_date', new_end_date);
                              genro.dlg.alert('Date range limited to 7 days. End date adjusted.', 'Warning');
                          }
                        }""",start_date='^.start_date',
                        end_date='^.end_date')
        fb.button('Search', margin_top='5px').dataRpc(
                  'main.results', self.get_neo_feed,
                  start_date='=.start_date',
                  end_date='=.end_date',_lockScreen=True)



        center = bc.contentPane(region='center')
        eb2 = center.expandbox(title='Results', open=True, animate=True,
                               height='100%')
        grid = eb2.quickGrid(value='^main.results', height='100%')
        grid.column(name='Name', field='name', width='15em')
        grid.column(name='Date', field='close_approach_date', width='8em')
        grid.column(name='Diameter (m)', field='diameter_min', width='8em',
                    dtype='N')
        grid.column(name='Diameter max (m)', field='diameter_max', width='8em',
                    dtype='N')
        grid.column(name='Velocity (km/h)', field='velocity_kmh', width='10em',
                    dtype='N')
        grid.column(name='Miss Distance (km)', field='miss_distance_km',
                    width='12em', dtype='N')
        grid.column(name='Hazardous', field='is_hazardous', width='6em')

    def _get_api_key(self):
        return self.application.config['nasa?api_key'] or 'DEMO_KEY'

    @public_method
    def get_neo_feed(self, start_date=None, end_date=None, **kwargs):
        """Fetch NEO feed for a date range (max 7 days)."""
        if not start_date or not end_date:
            return Bag()
        if hasattr(start_date, 'strftime'):
            start_date = start_date.strftime('%Y-%m-%d')
        if hasattr(end_date, 'strftime'):
            end_date = end_date.strftime('%Y-%m-%d')

        api_key = self._get_api_key()
        resolver = JsonRestResolver(
            f'{NEOWS_BASE}/feed',
            cacheTime=300,
            start_date=start_date,
            end_date=end_date,
            api_key=api_key
        )
        data = resolver()
        if 'error' in data.keys():
            return data
        result = Bag()
        i = 0
        neo_objects = data['near_earth_objects']
        for date_key in neo_objects.keys():
            day_bag = neo_objects[date_key]
            for neo_key in day_bag.keys():
                neo = day_bag[neo_key]
                diameter = neo['estimated_diameter.meters']
                approach = neo['close_approach_data.r_0'] if 'close_approach_data' in neo.keys() else None
                result.setItem(f'r_{i}', None,
                    name=neo['name'],
                    close_approach_date=date_key,
                    diameter_min=round(float(diameter['estimated_diameter_min']), 1) if diameter else None,
                    diameter_max=round(float(diameter['estimated_diameter_max']), 1) if diameter else None,
                    velocity_kmh=round(float(approach['relative_velocity.kilometers_per_hour']), 1) if approach else None,
                    miss_distance_km=round(float(approach['miss_distance.kilometers']), 1) if approach else None,
                    is_hazardous='Yes' if neo['is_potentially_hazardous_asteroid'] else 'No'
                )
                i += 1
        return result
