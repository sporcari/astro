#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent


class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('@fetch_id.@asteroid_id.name',
                    name='!!Asteroid', width='15em')
        r.fieldcell('@fetch_id.fetched_at',
                    name='!!Fetched at', width='12em')
        r.fieldcell('epoch_jd', width='14em', format='#,###.#########')
        r.fieldcell('epoch_cal', width='18em')
        r.fieldcell('x', width='12em', format='#,###.000000')
        r.fieldcell('y', width='12em', format='#,###.000000')
        r.fieldcell('z', width='12em', format='#,###.000000')
        r.fieldcell('vx', width='10em', format='#,###.000000')
        r.fieldcell('vy', width='10em', format='#,###.000000')
        r.fieldcell('vz', width='10em', format='#,###.000000')
        r.fieldcell('light_time', width='8em', format='#,###.000')
        r.fieldcell('range_au', width='10em', format='#,###.000000')
        r.fieldcell('range_rate', width='10em', format='#,###.000000')

    def th_order(self):
        return '@fetch_id.fetched_at desc,epoch_jd'

    def th_query(self):
        return dict(column='@fetch_id.@asteroid_id.name',
                    op='contains', val='')


class ViewFromFetch(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('epoch_jd', width='14em', format='#,###.#########')
        r.fieldcell('epoch_cal', width='18em')
        r.fieldcell('x', width='12em', format='#,###.000000')
        r.fieldcell('y', width='12em', format='#,###.000000')
        r.fieldcell('z', width='12em', format='#,###.000000')
        r.fieldcell('vx', width='10em', format='#,###.000000')
        r.fieldcell('vy', width='10em', format='#,###.000000')
        r.fieldcell('vz', width='10em', format='#,###.000000')
        r.fieldcell('light_time', width='8em', format='#,###.000')
        r.fieldcell('range_au', width='10em', format='#,###.000000')
        r.fieldcell('range_rate', width='10em', format='#,###.000000')

    def th_order(self):
        return 'epoch_jd'


class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        pane = bc.contentPane(region='center', datapath='.record',
                              padding='10px')
        fb = pane.formbuilder(cols=2, border_spacing='4px',
                              fld_width='100%')
        fb.field('fetch_id', colspan=2)
        fb.field('epoch_cal')
        fb.field('epoch_jd')
        fb.field('x')
        fb.field('y')
        fb.field('z')
        fb.field('vx')
        fb.field('vy')
        fb.field('vz')
        fb.field('light_time')
        fb.field('range_au')
        fb.field('range_rate')

    def th_options(self):
        return dict(dialog_height='600px', dialog_width='720px')
