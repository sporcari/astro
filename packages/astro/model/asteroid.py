#!/usr/bin/env python
# encoding: utf-8


class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('asteroid', pkey='id',
                        name_long='!!Asteroid',
                        name_plural='!!Asteroids',
                        caption_field='name')
        self.sysFields(tbl)
        tbl.column('neo_reference_id', name_long='!!NEO reference ID',
                   validate_notnull=True, unique=True)
        tbl.column('name', name_long='!!Name',
                   validate_notnull=True, unique=True)
        tbl.column('diameter_min', dtype='N',
                   name_long='!!Diameter min (m)',
                   name_short='Dmin')
        tbl.column('diameter_max', dtype='N',
                   name_long='!!Diameter max (m)',
                   name_short='Dmax')
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
