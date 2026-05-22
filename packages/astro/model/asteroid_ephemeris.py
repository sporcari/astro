#!/usr/bin/env python
# encoding: utf-8


class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('asteroid_ephemeris', pkey='id',
                        name_long='!!Asteroid ephemeris',
                        name_plural='!!Asteroid ephemerides')
        self.sysFields(tbl)
        tbl.column('asteroid_id', size='22', group='_',
                   name_long='!!Asteroid').relation(
                       'asteroid.id',
                       relation_name='ephemerides',
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
        tbl.column('center',
                   name_long='!!Center')
        tbl.column('ref_system',
                   name_long='!!Reference system')
        tbl.column('out_units',
                   name_long='!!Units')
        tbl.column('fetched_at', dtype='DHZ',
                   name_long='!!Fetched at')
        tbl.compositeColumn('ephem_point',
                            columns='asteroid_id,epoch_jd,center,ref_system,out_units',
                            unique=True)
        tbl.index('asteroid_id,epoch_jd', unique=False)
