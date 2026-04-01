#!/usr/bin/env python
# encoding: utf-8

class Menu(object):
    def config(self, root):
        astro = root.branch("Astro")
        astro.webpage('ISS Tracker', filepath='/astro/iss_tracker')
        root.packageBranch("Admin", pkg='adm', tags="admin")
        root.packageBranch("System", pkg='sys', tags="admin")
