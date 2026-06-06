#!/usr/bin/env python
# encoding: utf-8

class Menu(object):
    def config(self, root):
        pages = root.branch("Pages")
        pages.webpage('ISS Tracker', filepath='/astro/iss_tracker')
        pages.webpage('NeoWs - Asteroids', filepath='/astro/neows')
        pages.webpage('NEO History (Lookup)', filepath='/astro/neo_history')
        pages.webpage('Horizons Ephemeris', filepath='/astro/horizons')
        pages.webpage('3D Trajectory', filepath='/astro/trajectory')

        tables = root.branch("Tables")
        tables.thpage('Asteroids', table='astro.asteroid')
        tables.thpage('Asteroid approaches', table='astro.asteroid_approach')
        tables.thpage('Fetches', table='astro.asteroid_fetch')
        tables.thpage('Ephemerides', table='astro.asteroid_ephemeris')

        root.packageBranch("Admin", pkg='adm', tags="admin")
        root.packageBranch("System", pkg='sys', tags="admin")
