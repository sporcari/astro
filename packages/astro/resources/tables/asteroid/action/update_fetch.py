# -*- coding: utf-8 -*-

from gnr.web.batch.btcaction import BaseResourceAction
from gnr.core.gnrbag import Bag
#from gnr.core.gnrstring import flatten
#from collections import defaultdict
from datetime import datetime, timezone
#import uuid
from resolvers import JsonRestResolver

caption = "Fetch asteroid"

HORIZONS_URL = 'https://ssd.jpl.nasa.gov/api/horizons.api'

CENTER_OPTIONS = ('500@399:Geocentric,'
                  '500@10:Heliocentric,'
                  '500@0:Solar System Barycenter')
STEP_UNIT_OPTIONS = 'd:days,h:hours,m:minutes'
OUT_UNITS_OPTIONS = 'KM-S:km / km/s,AU-D:AU / AU/day,KM-D:km / km/day'
REF_SYSTEM_OPTIONS = 'ICRF:ICRF,B1950:B1950'

class Main(BaseResourceAction):
    batch_prefix = 'esporta_files_note_spese'
    batch_title = caption
    
    def pre_process(self):
        self.selection = self.get_selection(columns='*')
        self.fetches_tbl = self.db.table('astro.asteroid_fetch')
        self.now = datetime.now()
        
    def do(self):
        for ns in self.btc.thermo_wrapper(self.selection, message='Fetch', maximum=len(self.selection)):
            self.fetch_ephemeris(asteroid_id=ns['id'],
                neo_reference_id=ns['neo_reference_id'],
                start_time=self.batch_parameters.get('start_time',self.now),
                stop_time=self.batch_parameters.get('stop_time',self.now),
                step_value=self.batch_parameters.get('step_value', 1),
                step_unit=self.batch_parameters.get('step_unit', 'd'),
                center=self.batch_parameters.get('center', '500@399'),
                out_units=self.batch_parameters.get('out_units', 'KM-S'),
                ref_system=self.batch_parameters.get('ref_system', 'ICRF')
            )
        self.db.commit()
    
    def table_script_parameters_pane(self, pane, **kwargs):
        fb = pane.formbuilder(cols=2, border_spacing='3px')
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