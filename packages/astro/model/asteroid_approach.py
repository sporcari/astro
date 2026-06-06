#!/usr/bin/env python
# encoding: utf-8


class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('asteroid_approach', pkey='id',
                        name_long='!!Asteroid approach',
                        name_plural='!!Asteroid approaches')
        self.sysFields(tbl)
        tbl.column('asteroid_id', size='22', group='_',
                   name_long='!!Asteroid').relation(
                       'asteroid.id',
                       relation_name='approaches',
                       mode='foreignkey',
                       onDelete='cascade')
        tbl.column('close_approach_date', dtype='D',
                   name_long='!!Close approach date')
        tbl.column('close_approach_date_full',
                   name_long='!!Close approach date (full)')
        tbl.column('epoch_date_close_approach', dtype='L',
                   name_long='!!Epoch (ms)')
        tbl.column('relative_velocity_kms', dtype='N',
                   name_long='!!Velocity (km/s)')
        tbl.column('relative_velocity_kmh', dtype='N',
                   name_long='!!Velocity (km/h)')
        tbl.column('relative_velocity_mph', dtype='N',
                   name_long='!!Velocity (mph)')
        tbl.column('miss_distance_astronomical', dtype='N',
                   name_long='!!Miss distance (AU)')
        tbl.column('miss_distance_lunar', dtype='N',
                   name_long='!!Miss distance (lunar)')
        tbl.column('miss_distance_km', dtype='N',
                   name_long='!!Miss distance (km)')
        tbl.column('miss_distance_miles', dtype='N',
                   name_long='!!Miss distance (miles)')
        tbl.column('orbiting_body',
                   name_long='!!Orbiting body')
        tbl.column('is_hazardous', dtype='B',
                   name_long='!!Hazardous')
        tbl.column('sampled_at', dtype='DHZ',
                   name_long='!!Sampled at')
        tbl.index('asteroid_id,sampled_at', unique=False)


    def write_approach(self, asteroid_id=None, ap=None, sampled_at=None):
        velocity = ap['relative_velocity']
        miss = ap['miss_distance']
        ap_date = ap['close_approach_date']
        epoch = int(ap['epoch_date_close_approach']) if ap['epoch_date_close_approach'] else None
        miss_km = float(miss['kilometers']) if miss else None
        vel_kms = float(velocity['kilometers_per_second']) if velocity else None
        if self._already_imported(asteroid_id, ap_date):
            return
            
        self.insert(self.newrecord(
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
            sampled_at=sampled_at,
        ))

    def _already_imported(self, asteroid_id, ap_date):
        last = self.query(
            where='$asteroid_id=:aid AND $close_approach_date=:cad',
            aid=asteroid_id, cad=ap_date,
            columns='$epoch_date_close_approach,$miss_distance_km,$relative_velocity_kms',
            order_by='$sampled_at desc', limit=1).fetch()
        
        if last:
            return True
        
