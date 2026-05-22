# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, timezone
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
        fb = eb.formlet(datapath='.parameters', cols=4)
        fb.dateTextBox(value='^.start_date', lbl='Start Date', width='12em',
                       period_to='.end_date')
       
        fb.horizontalSlider(value='^.period', lbl='Day shift',
                            minimum=0, maximum=7, discreteValues=0,
                            width='75%',
                            default=0,
                            intermediateChanges=False,
                            tooltip='Shift end date by N days from start date.')
        fb.dateTextBox(value='^.end_date', lbl='End Date', width='12em', readOnly=True)
        fb.dataController("""
                        if (start_date && period!=null){
                            var new_end_date = new Date(start_date.getTime() + period*86400000);
                            this.setRelativeData('.end_date', new_end_date);
                        }""",start_date='^.start_date',
                        end_date='^.end_date',
                        period='^.period')
        fb.dataRpc(
                  'main.results', self.get_neo_feed,
                  start_date='=.start_date',
                  end_date='^.end_date',_lockScreen=True)



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
                self._persist_neo(neo, date_key)
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
        self.db.commit()
        return result

    def _persist_neo(self, neo, date_key):
        diameter = neo['estimated_diameter.meters']
        is_hazardous = bool(neo['is_potentially_hazardous_asteroid'])
        asteroid_tbl = self.db.table('astro.asteroid')
        neo_ref_id = neo['neo_reference_id'] or neo['id']
        with asteroid_tbl.recordToUpdate(neo_reference_id=neo_ref_id,
                                         insertMissing=True) as rec:
            rec['neo_reference_id'] = neo_ref_id
            rec['name'] = neo['name']
            if diameter:
                rec['diameter_min'] = round(float(diameter['estimated_diameter_min']), 3)
                rec['diameter_max'] = round(float(diameter['estimated_diameter_max']), 3)
        asteroid_id = rec['id']

        approaches = neo['close_approach_data'] if 'close_approach_data' in neo.keys() else None
        if not approaches:
            return
        approach_tbl = self.db.table('astro.asteroid_approach')
        sampled_at = datetime.now(timezone.utc)
        for ap_key in approaches.keys():
            ap = approaches[ap_key]
            velocity = ap['relative_velocity']
            miss = ap['miss_distance']
            ap_date = ap['close_approach_date'] or date_key
            epoch = int(ap['epoch_date_close_approach']) if ap['epoch_date_close_approach'] else None
            miss_km = float(miss['kilometers']) if miss else None
            vel_kms = float(velocity['kilometers_per_second']) if velocity else None
            if self._approach_is_unchanged(approach_tbl, asteroid_id, ap_date,
                                           epoch, miss_km, vel_kms):
                continue
            approach_tbl.insert(approach_tbl.newrecord(
                asteroid_id=asteroid_id,
                close_approach_date=ap_date,
                close_approach_date_full=ap['close_approach_date_full'],
                epoch_date_close_approach=epoch,
                relative_velocity_kms=vel_kms,
                relative_velocity_kmh=float(velocity['kilometers_per_hour']) if velocity else None,
                relative_velocity_mph=float(velocity['miles_per_hour']) if velocity else None,
                miss_distance_astronomical=float(miss['astronomical']) if miss else None,
                miss_distance_lunar=float(miss['lunar']) if miss else None,
                miss_distance_km=miss_km,
                miss_distance_miles=float(miss['miles']) if miss else None,
                orbiting_body=ap['orbiting_body'],
                is_hazardous=is_hazardous,
                sampled_at=sampled_at,
            ))

    def _approach_is_unchanged(self, approach_tbl, asteroid_id, ap_date,
                               epoch, miss_km, vel_kms):
        last = approach_tbl.query(
            where='$asteroid_id=:aid AND $close_approach_date=:cad',
            aid=asteroid_id, cad=ap_date,
            columns='$epoch_date_close_approach,$miss_distance_km,$relative_velocity_kms',
            order_by='$sampled_at desc', limit=1).fetch()
        if not last:
            return False
        prev = last[0]
        prev_miss = float(prev['miss_distance_km']) if prev['miss_distance_km'] is not None else None
        prev_vel = float(prev['relative_velocity_kms']) if prev['relative_velocity_kms'] is not None else None
        return (prev['epoch_date_close_approach'] == epoch
                and prev_miss == miss_km
                and prev_vel == vel_kms)
