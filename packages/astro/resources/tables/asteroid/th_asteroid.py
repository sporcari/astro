#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent


class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('neo_reference_id', width='10em')
        r.fieldcell('name', width='15em')
        r.fieldcell('diameter_min', width='8em', format='#,###.00')
        r.fieldcell('diameter_max', width='8em', format='#,###.00')
        r.fieldcell('approach_count', width='6em')
        r.fieldcell('last_approach_date', width='10em')

    def th_order(self):
        return 'name'

    def th_query(self):
        return dict(column='name', op='contains', val='')


class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        self.asteroidData(bc.roundedGroupFrame(
            title='!!Asteroid', region='top',
            datapath='.record', height='130px'))
        bc.contentPane(region='center', margin='2px').plainTableHandler(
            relation='@approaches', viewResource='ViewFromAsteroid')

    def asteroidData(self, pane):
        fb = pane.div(margin='10px').formbuilder(
            cols=3, border_spacing='4px', fld_width='100%')
        fb.field('neo_reference_id', colspan=3)
        fb.field('name', validate_notnull=True, colspan=3)
        fb.field('diameter_min')
        fb.field('diameter_max')

    def th_options(self):
        return dict(dialog_height='550px', dialog_width='900px')
