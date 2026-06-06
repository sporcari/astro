#!/usr/bin/env python
# encoding: utf-8


class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('asteroid_fetch', pkey='id',
                        name_long='!!Asteroid fetch',
                        caption_field='asteroid_id',
                        name_plural='!!Asteroid fetches')
        self.sysFields(tbl, counter='asteroid_id')
        tbl.column('asteroid_id', size='22', group='_',
                   name_long='!!Asteroid').relation(
                       'asteroid.id',
                       relation_name='fetches',
                       mode='foreignkey',
                       onDelete='cascade')
        tbl.column('start_time', dtype='D', name_long='!!Start date')
        tbl.column('stop_time', dtype='D', name_long='!!Stop date')
        tbl.column('step_value', dtype='I', name_long='!!Step')
        tbl.column('step_unit', size=':2', name_long='!!Step unit')
        tbl.column('center', size=':16', name_long='!!Center')
        tbl.column('out_units', size=':8', name_long='!!Units')
        tbl.column('ref_system', size=':8', name_long='!!Ref system')
        tbl.column('fetched_at', dtype='DHZ', name_long='!!Fetched at')
        tbl.formulaColumn('caption', "@asteroid_id.name||' - '|| $_row_count||' — '||$fetched_at",
                           name_long='!!Caption')
        tbl.formulaColumn('point_count',
                          select=dict(table='astro.asteroid_ephemeris',
                                      columns='COUNT(*)',
                                      where='$fetch_id=#THIS.id'),
                          dtype='L', name_long='!!Points')
 