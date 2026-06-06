# -*- coding: utf-8 -*-

from datetime import datetime, timezone
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
from resolvers import JsonRestResolver

HORIZONS_URL = 'https://ssd.jpl.nasa.gov/api/horizons.api'

CENTER_OPTIONS = ('500@399:Geocentric,'
                  '500@10:Heliocentric,'
                  '500@0:Solar System Barycenter')
STEP_UNIT_OPTIONS = 'd:days,h:hours,m:minutes'
OUT_UNITS_OPTIONS = 'KM-S:km / km/s,AU-D:AU / AU/day,KM-D:km / km/day'
REF_SYSTEM_OPTIONS = 'ICRF:ICRF,B1950:B1950'


class GnrCustomWebPage(object):

    def main(self, root, **kwargs):
        bc = root.borderContainer(datapath='main', padding='10px')

        top = bc.contentPane(region='top')
        eb = top.expandbox(title='Horizons Ephemeris Query',
                           open=True, animate=True)
        fb = eb.formlet(datapath='.parameters', cols=4)
        fb.dbselect(value='^.neo_reference_id', table='astro.asteroid',
                    alternatePkey='neo_reference_id',
                    selected_id='.asteroid_id',
                    auxColumns='$diameter_min,$diameter_max',
                    hasDownArrow=True,
                    lbl='Asteroid', validate_notnull=True, colspan=4)
        fb.dateTextBox(value='^.start_time', lbl='Start date', width='11em')
        fb.dateTextBox(value='^.stop_time', lbl='Stop date', width='11em')
        fb.numberTextBox(value='^.step_value', lbl='Step', default=1,
                         width='5em')
        fb.filteringSelect(value='^.step_unit', values=STEP_UNIT_OPTIONS,
                           lbl='Step unit', default='h', width='8em')
        fb.filteringSelect(value='^.center', values=CENTER_OPTIONS,
                           lbl='Center', default='500@399', width='16em',
                           colspan=2)
        fb.filteringSelect(value='^.out_units', values=OUT_UNITS_OPTIONS,
                           lbl='Units', default='KM-S', width='12em')
        fb.filteringSelect(value='^.ref_system', values=REF_SYSTEM_OPTIONS,
                           lbl='Ref system', default='ICRF', width='8em')
        fb.button('Fetch ephemeris').dataRpc(
            'main.results', self.fetch_ephemeris,
            asteroid_id='=.asteroid_id',
            neo_reference_id='=.neo_reference_id',
            start_time='=.start_time',
            stop_time='=.stop_time',
            step_value='=.step_value',
            step_unit='=.step_unit',
            center='=.center',
            out_units='=.out_units',
            ref_system='=.ref_system', _lockScreen=True)
        fb.div(value='^main.results.error', colspan=3,
               hidden='^main.results.error?=!#v',
               color='red', font_weight='bold', padding='4px')

        center = bc.contentPane(region='center')
        eb2 = center.expandbox(title='Ephemeris', open=True,
                               animate=True, height='100%')
        grid = eb2.quickGrid(value='^main.results.data', height='100%')
        grid.column(name='Epoch (JD)', field='epoch_jd', width='14em',
                    dtype='N', format='#,###.#########')
        grid.column(name='Calendar', field='epoch_cal', width='18em')
        grid.column(name='X', field='x', width='12em', dtype='N')
        grid.column(name='Y', field='y', width='12em', dtype='N')
        grid.column(name='Z', field='z', width='12em', dtype='N')
        grid.column(name='VX', field='vx', width='10em', dtype='N')
        grid.column(name='VY', field='vy', width='10em', dtype='N')
        grid.column(name='VZ', field='vz', width='10em', dtype='N')
        grid.column(name='Range', field='range_au', width='10em', dtype='N')
        grid.column(name='Range rate', field='range_rate', width='10em',
                    dtype='N')

    @public_method
    def fetch_ephemeris(self, asteroid_id=None, neo_reference_id=None,
                        start_time=None, stop_time=None,
                        step_value=1, step_unit='h',
                        center='500@399', out_units='KM-S',
                        ref_system='ICRF', **kwargs):
        result = Bag()
        if not (asteroid_id and neo_reference_id and start_time and stop_time):
            result['error'] = 'Missing required parameters'
            return result

        if hasattr(start_time, 'strftime'):
            start_time = start_time.strftime('%Y-%m-%d')
        if hasattr(stop_time, 'strftime'):
            stop_time = stop_time.strftime('%Y-%m-%d')

        resolver = JsonRestResolver(
            HORIZONS_URL,
            cacheTime=300,
            format='json',
            COMMAND=f"'DES={neo_reference_id};'",
            EPHEM_TYPE='VECTORS',
            CENTER=f"'{center}'",
            START_TIME=f"'{start_time}'",
            STOP_TIME=f"'{stop_time}'",
            STEP_SIZE=f"'{step_value}{step_unit}'",
            OUT_UNITS=out_units,
            REF_SYSTEM=ref_system,
            VEC_TABLE='3',
            CSV_FORMAT='YES',
            OBJ_DATA='NO',
            MAKE_EPHEM='YES',
        )
        data = resolver()
        if 'error' in data.keys():
            result['error'] = data['error']
            return result
        raw = data['result']
        if not raw or '$$SOE' not in raw:
            result['error'] = raw or 'No ephemeris returned'
            return result

        rows = self._parse_vectors(raw)
        if not rows:
            result['error'] = 'No rows parsed from Horizons response'
            return result

        fetch_id = self._create_fetch(
            asteroid_id=asteroid_id,
            start_time=start_time, stop_time=stop_time,
            step_value=step_value, step_unit=step_unit,
            center=center, out_units=out_units, ref_system=ref_system)
        self._persist(fetch_id, rows)
        self.db.commit()

        display = Bag()
        for i, row in enumerate(rows):
            display.setItem(f'r_{i}', None, **row)
        result['data'] = display
        return result

    def _parse_vectors(self, text):
        start = text.index('$$SOE') + len('$$SOE')
        end = text.index('$$EOE')
        block = text[start:end].strip()
        rows = []
        for line in block.splitlines():
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 8 or not parts[0]:
                continue
            try:
                row = dict(
                    epoch_jd=float(parts[0]),
                    epoch_cal=parts[1],
                    x=float(parts[2]),
                    y=float(parts[3]),
                    z=float(parts[4]),
                    vx=float(parts[5]),
                    vy=float(parts[6]),
                    vz=float(parts[7]),
                )
                if len(parts) >= 11:
                    row['light_time'] = float(parts[8])
                    row['range_au'] = float(parts[9])
                    row['range_rate'] = float(parts[10])
                rows.append(row)
            except (ValueError, IndexError):
                continue
        return rows

    def _create_fetch(self, asteroid_id, start_time, stop_time,
                      step_value, step_unit, center, out_units, ref_system):
        tbl = self.db.table('astro.asteroid_fetch')
        rec = tbl.insert(tbl.newrecord(
            asteroid_id=asteroid_id,
            start_time=start_time,
            stop_time=stop_time,
            step_value=int(step_value) if step_value is not None else None,
            step_unit=step_unit,
            center=center,
            out_units=out_units,
            ref_system=ref_system,
            fetched_at=datetime.now(timezone.utc),
        ))
        return rec['id']

    def _persist(self, fetch_id, rows):
        tbl = self.db.table('astro.asteroid_ephemeris')
        for row in rows:
            tbl.insert(tbl.newrecord(fetch_id=fetch_id, **row))
