#!/usr/bin/env python
# encoding: utf-8

class Menu(object):
    def config(self, root):
        astro = root.branch("Astro")
        astro.webpage('ISS Tracker', filepath='/astro/iss_tracker')
        nasa = root.branch("NASA APIs")
        nasa.webpage('NeoWs - Asteroids', filepath='/astro/neows')
        nasa.thpage('Asteroids', table='astro.asteroid')
        nasa.thpage('Asteroid approaches', table='astro.asteroid_approach')
        nasa.webpage('Horizons Ephemeris', filepath='/astro/horizons')
        nasa.thpage('Ephemerides', table='astro.asteroid_ephemeris')
        root.packageBranch("Admin", pkg='adm', tags="admin")
        root.packageBranch("System", pkg='sys', tags="admin")
