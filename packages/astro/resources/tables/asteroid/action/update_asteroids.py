# -*- coding: utf-8 -*-

from gnr.web.batch.btcaction import BaseResourceAction
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import flatten
from collections import defaultdict
from datetime import datetime
import uuid

caption = 'Update asteroids data from NASA NEO API'

class Main(BaseResourceAction):
    batch_prefix = 'esporta_files_note_spese'
    batch_title = caption
       
    def pre_process(self):
        self.selection = self.get_selection(columns='*')
        self.asteroid_tbl = self.db.table('astro.asteroid')
        self.approach_tbl = self.db.table('astro.asteroid_approach')
        self.now = datetime.now()

    def do(self):
        for ns in self.btc.thermo_wrapper(self.selection, message='Asteroids', maximum=len(self.selection)):
            if ns['orbit_id']:
                continue
            neo_reference_id = ns['neo_reference_id']
            asteroid_id = ns['id']
            data = self.asteroid_tbl.fetch_history(asteroid_id=asteroid_id, neo_ref=neo_reference_id)
            self.asteroid_tbl.update_history(data=data, asteroid_id=asteroid_id)
            approaches = data['close_approach_data']
            if not approaches or not approaches.keys():
                continue
            for ap_key in approaches.keys():
                ap = approaches[ap_key]
                self.approach_tbl.write_approach(asteroid_id=asteroid_id, ap= ap, sampled_at=self.now)
            #close_approach_data = self.batch_parameters['close_approach_data']
        self.db.commit()
    # ----------------------------
    # UI params (placeholder)
    # ----------------------------
    def table_script_parameters_pane(self, pane, **kwargs):
        fb = pane.formbuilder(cols=1, border_spacing='3px')
        fb.div('Confirm?')

    #TO ADD MORE?
