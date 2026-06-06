#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent


class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('@asteroid_id.name', name='!!Asteroid', width='15em')
        r.fieldcell('_row_count', name='!!#', width='4em')
        r.fieldcell('fetched_at', width='12em')
        r.fieldcell('start_time', width='9em')
        r.fieldcell('stop_time', width='9em')
        r.fieldcell('step_value', width='4em')
        r.fieldcell('step_unit', width='4em')
        r.fieldcell('center', width='10em')
        r.fieldcell('out_units', width='6em')
        r.fieldcell('ref_system', width='6em')
        r.fieldcell('point_count', width='6em')

    def th_order(self):
        return 'fetched_at desc'

    def th_query(self):
        return dict(column='@asteroid_id.name', op='contains', val='')


class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        self.fetchData(bc.roundedGroupFrame(
            title='!!Fetch parameters', region='top',
            datapath='.record', height='240px'))
        bc.contentPane(region='center', margin='2px').plainTableHandler(
            relation='@points', viewResource='ViewFromFetch')

    def fetchData(self, pane):
        fb = pane.div(margin='10px').formbuilder(
            cols=2, border_spacing='4px', fld_width='100%')
        fb.field('asteroid_id', colspan=2)
        fb.field('fetched_at')
        fb.field('_row_count', readOnly=True, lbl='!!Fetch #')
        fb.field('start_time')
        fb.field('stop_time')
        fb.field('step_value')
        fb.field('step_unit')
        fb.field('center')
        fb.field('out_units')
        fb.field('ref_system')

    def th_options(self):
        return dict(dialog_height='600px', dialog_width='900px')
