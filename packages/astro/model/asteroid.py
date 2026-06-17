#!/usr/bin/env python
# encoding: utf-8

from datetime import datetime, timezone
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method



class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('asteroid', pkey='id',
                        name_long='!!Asteroid',
                        name_plural='!!Asteroids',
                        caption_field='name')
        self.sysFields(tbl)

        # Anagrafica
        tbl.column('neo_reference_id', name_long='!!NEO reference ID',
                   validate_notnull=True, unique=True)
        tbl.column('name', name_long='!!Name',
                   validate_notnull=True, unique=True)
        g_id = tbl.colgroup('identity', name_long='!!Identity')
        g_id.column('name_limited', name_long='!!Short name')
        g_id.column('designation', name_long='!!Designation')
        g_id.column('nasa_jpl_url', dtype='P', name_long='!!JPL link')

        # Caratteristiche fisiche
        g_phys = tbl.colgroup('physical', name_long='!!Physical')
        g_phys.column('diameter_min', dtype='N',
                      name_long='!!Diameter min (m)', name_short='Dmin')
        g_phys.column('diameter_max', dtype='N',
                      name_long='!!Diameter max (m)', name_short='Dmax')
        g_phys.column('absolute_magnitude_h', dtype='N',
                      name_long='!!Abs. magnitude (H)')

        # Flags di rischio
        g_haz = tbl.colgroup('hazard', name_long='!!Hazard flags')
        g_haz.column('is_potentially_hazardous', dtype='B',
                     name_long='!!Hazardous')
        g_haz.column('is_sentry_object', dtype='B',
                     name_long='!!Sentry')

        # Classe orbitale (testuale)
        g_class = tbl.colgroup('orbit_class', name_long='!!Orbit class')
        g_class.column('orbit_class_type', name_long='!!Class type')
        g_class.column('orbit_class_description', dtype='T',
                       name_long='!!Class description')
        g_class.column('orbit_class_range', dtype='T',
                       name_long='!!Class range')

        # Metadati della determinazione orbitale
        g_meta = tbl.colgroup('orbit_meta',
                              name_long='!!Orbit determination')
        g_meta.column('orbit_id', name_long='!!Orbit ID')
        g_meta.column('orbit_determination_date', dtype='DHZ',
                      name_long='!!Determination date')
        g_meta.column('first_observation_date', dtype='D',
                      name_long='!!First observation')
        g_meta.column('last_observation_date', dtype='D',
                      name_long='!!Last observation')
        g_meta.column('data_arc_in_days', dtype='L',
                      name_long='!!Data arc (days)')
        g_meta.column('observations_used', dtype='L',
                      name_long='!!Observations used')
        g_meta.column('orbit_uncertainty', name_long='!!Uncertainty')
        g_meta.column('equinox', name_long='!!Equinox')
        g_meta.column('epoch_osculation', dtype='N',
                      name_long='!!Epoch osculation (JD)')

        # Elementi Kepleriani
        g_kep = tbl.colgroup('kepler', name_long='!!Keplerian elements')
        g_kep.column('eccentricity', dtype='N', name_long='!!Eccentricity')
        g_kep.column('semi_major_axis', dtype='N',
                     name_long='!!Semi-major axis (AU)')
        g_kep.column('inclination', dtype='N',
                     name_long='!!Inclination (°)')
        g_kep.column('ascending_node_longitude', dtype='N',
                     name_long='!!Ascending node long. (°)')
        g_kep.column('perihelion_argument', dtype='N',
                     name_long='!!Perihelion argument (°)')
        g_kep.column('mean_anomaly', dtype='N',
                     name_long='!!Mean anomaly (°)')
        g_kep.column('mean_motion', dtype='N',
                     name_long='!!Mean motion (°/day)')
        g_kep.column('perihelion_distance', dtype='N',
                     name_long='!!Perihelion (AU)')
        g_kep.column('aphelion_distance', dtype='N',
                     name_long='!!Aphelion (AU)')
        g_kep.column('perihelion_time', dtype='N',
                     name_long='!!Perihelion time (JD)')
        g_kep.column('orbital_period', dtype='N',
                     name_long='!!Orbital period (days)')

        # Metriche derivate / di rischio
        g_der = tbl.colgroup('derived', name_long='!!Derived metrics')
        g_der.column('moid', dtype='N',
                     name_long='!!MOID Earth (AU)')
        g_der.column('jupiter_tisserand_invariant', dtype='N',
                     name_long='!!Tisserand (Jupiter)')

        # Formula columns
        tbl.formulaColumn('approach_count',
                          select=dict(table='astro.asteroid_approach',
                                      columns='COUNT(*)',
                                      where='$asteroid_id=#THIS.id'),
                          dtype='L', name_long='!!Approach count')
        tbl.formulaColumn('last_approach_date',
                          select=dict(table='astro.asteroid_approach',
                                      columns='MAX($close_approach_date)',
                                      where='$asteroid_id=#THIS.id'),
                          dtype='D', name_long='!!Last approach')
        tbl.formulaColumn('has_ephemeris',
                          exists=dict(table='astro.asteroid_fetch',
                                      where='$asteroid_id=#THIS.id'),
                          dtype='B', name_long='!!Has ephemeris')
        
    def update_history(self, data=None, asteroid_id=None):

        diameter = data['estimated_diameter.meters']
        orbital = data['orbital_data']
        with self.recordToUpdate(pkey=asteroid_id) as ast:
            if diameter:
                dmin = diameter['estimated_diameter_min']
                dmax = diameter['estimated_diameter_max']
                if dmin is not None:
                    ast['diameter_min'] = round(float(dmin), 3)
                if dmax is not None:
                    ast['diameter_max'] = round(float(dmax), 3)
            ast['name_limited'] = data['name_limited']
            ast['designation'] = data['designation']
            ast['nasa_jpl_url'] = data['nasa_jpl_url']
            ast['absolute_magnitude_h'] = self._as_float(data['absolute_magnitude_h'])
            ast['is_potentially_hazardous'] = bool(data['is_potentially_hazardous_asteroid'])
            ast['is_sentry_object'] = bool(data['is_sentry_object'])
            if orbital:
                self._fill_orbital(ast, orbital)

    

    def _as_float(self, v):
        if v is None:
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    def _as_int(self, v):
        if v is None:
            return None
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    def _fill_orbital(self, ast, orbital):
        # Numeric Keplerian elements
        for k in ('eccentricity', 'semi_major_axis', 'inclination',
                  'ascending_node_longitude', 'perihelion_argument',
                  'mean_anomaly', 'mean_motion',
                  'perihelion_distance', 'aphelion_distance',
                  'perihelion_time', 'orbital_period',
                  'epoch_osculation', 'jupiter_tisserand_invariant'):
            ast[k] = self._as_float(orbital[k])
        ast['moid'] = self._as_float(orbital['minimum_orbit_intersection'])
        ast['data_arc_in_days'] = self._as_int(orbital['data_arc_in_days'])
        ast['observations_used'] = self._as_int(orbital['observations_used'])
        # Text / date fields
        ast['orbit_id'] = orbital['orbit_id']
        ast['orbit_uncertainty'] = orbital['orbit_uncertainty']
        ast['equinox'] = orbital['equinox']
        ast['orbit_determination_date'] = orbital['orbit_determination_date']
        ast['first_observation_date'] = orbital['first_observation_date']
        ast['last_observation_date'] = orbital['last_observation_date']
        # Orbit class sub-object
        orbit_class = orbital['orbit_class']
        if orbit_class:
            ast['orbit_class_type'] = orbit_class['orbit_class_type']
            ast['orbit_class_description'] = orbit_class['orbit_class_description']
            ast['orbit_class_range'] = orbit_class['orbit_class_range']

