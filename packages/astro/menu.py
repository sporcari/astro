#!/usr/bin/env python
# encoding: utf-8

class Menu(object):
    def config(self, root):
        root.packageBranch("Admin", pkg='adm', tags="admin")
        root.packageBranch("System", pkg='sys', tags="admin")
