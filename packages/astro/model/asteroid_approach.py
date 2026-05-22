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
