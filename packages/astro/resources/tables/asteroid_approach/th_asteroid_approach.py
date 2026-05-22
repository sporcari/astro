#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent


class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('@asteroid_id.name', name='!!Asteroid', width='15em')
        r.fieldcell('sampled_at', width='12em')
        r.fieldcell('close_approach_date', width='10em')
        r.fieldcell('close_approach_date_full', width='12em')
        r.fieldcell('relative_velocity_kmh', width='10em', format='#,###.00')
        r.fieldcell('miss_distance_km', width='12em', format='#,###.00')
        r.fieldcell('miss_distance_lunar', width='8em', format='#,###.00')
        r.fieldcell('orbiting_body', width='8em')
        r.fieldcell('is_hazardous', width='6em')

    def th_order(self):
        return 'sampled_at:d'

    def th_query(self):
        return dict(column='close_approach_date', op='equal', val='')


class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        pane = bc.contentPane(region='center', datapath='.record',
                              padding='10px')
        fb = pane.formbuilder(cols=2, border_spacing='4px',
                              fld_width='100%')
        fb.field('asteroid_id', colspan=2)
        fb.field('sampled_at')
        fb.field('close_approach_date')
        fb.field('close_approach_date_full')
        fb.field('epoch_date_close_approach')
        fb.field('relative_velocity_kms')
        fb.field('relative_velocity_kmh')
        fb.field('relative_velocity_mph')
        fb.field('miss_distance_km')
        fb.field('miss_distance_lunar')
        fb.field('miss_distance_astronomical')
        fb.field('miss_distance_miles')
        fb.field('orbiting_body')
        fb.field('is_hazardous')

    def th_options(self):
        return dict(dialog_height='550px', dialog_width='700px')


class ViewFromAsteroid(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('sampled_at', width='12em')
        r.fieldcell('close_approach_date', width='10em')
        r.fieldcell('close_approach_date_full', width='12em')
        r.fieldcell('relative_velocity_kms', width='9em', format='#,###.00')
        r.fieldcell('relative_velocity_kmh', width='10em', format='#,###.00')
        r.fieldcell('miss_distance_km', width='12em', format='#,###.00')
        r.fieldcell('miss_distance_lunar', width='8em', format='#,###.00')
        r.fieldcell('miss_distance_astronomical', width='8em', format='#,###.0000')
        r.fieldcell('orbiting_body', width='8em')
        r.fieldcell('is_hazardous', width='6em')

    def th_order(self):
        return 'sampled_at:d'
