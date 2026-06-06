#!/usr/bin/env python
# encoding: utf-8


class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('asteroid_ephemeris', pkey='id',
                        name_long='!!Asteroid ephemeris',
                        name_plural='!!Asteroid ephemerides')
        self.sysFields(tbl)
        tbl.column('fetch_id', size='22', group='_',
                   name_long='!!Fetch').relation(
                       'asteroid_fetch.id',
                       relation_name='points',
                       mode='foreignkey',
                       onDelete='cascade')
        tbl.column('epoch_jd', dtype='N', size='18,9',
                   name_long='!!Epoch (JD TDB)')
        tbl.column('epoch_cal',
                   name_long='!!Epoch (calendar)')
        tbl.column('x', dtype='N', name_long='!!X')
        tbl.column('y', dtype='N', name_long='!!Y')
        tbl.column('z', dtype='N', name_long='!!Z')
        tbl.column('vx', dtype='N', name_long='!!VX')
        tbl.column('vy', dtype='N', name_long='!!VY')
        tbl.column('vz', dtype='N', name_long='!!VZ')
        tbl.column('light_time', dtype='N',
                   name_long='!!Light time')
        tbl.column('range_au', dtype='N',
                   name_long='!!Range')
        tbl.column('range_rate', dtype='N',
                   name_long='!!Range rate')
        tbl.compositeColumn('fetch_point',
                            columns='fetch_id,epoch_jd',
                            unique=True)
