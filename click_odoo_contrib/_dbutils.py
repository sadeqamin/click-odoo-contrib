# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from contextlib import contextmanager

from click_odoo import odoo


@contextmanager
def pg_connect(dbname="postgres"):
    conn = odoo.sql_db.db_connect(dbname)
    cr = conn.cursor()
    cr.autocommit(True)
    try:
        yield cr._obj
    finally:
        cr.close()


def db_exists(dbname):
    with pg_connect() as cr:
        cr.execute(
            "SELECT datname FROM pg_catalog.pg_database "
            "WHERE lower(datname) = lower(%s)",
            (dbname,),
        )
        return bool(cr.fetchone())


def db_initialized(dbname):
    if not db_exists(dbname):
        return False
    with pg_connect(dbname) as cr:
        return odoo.modules.db.is_initialized(cr)


def terminate_connections(dbname):
    with pg_connect() as cr:
        cr.execute(
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "
            "FROM pg_stat_activity "
            "WHERE pg_stat_activity.datname = %s "
            "AND pid <> pg_backend_pid();",
            (dbname,),
        )


@contextmanager
def db_management_enabled():
    list_db = odoo.tools.config["list_db"]
    odoo.tools.config["list_db"] = True
    try:
        yield
    finally:
        odoo.tools.config["list_db"] = list_db
