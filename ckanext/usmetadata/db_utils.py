__author__ = 'ykhadilkar'

from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.sql import select, text
from sqlalchemy import func
import ckan.model as model

cached_tables = {}

def get_parent_organizations(limit=20):
    items = {}
    connection = model.Session.connection()
    res = connection.execute(
        text("""select package_id, title
                from package_extra, package
                where package_extra.key = 'is_parent' and package_extra.value = 'true' and package.id = package_extra.package_id""")).fetchmany(limit)
    for result in res:
        items[result._row[0]] = result._row[1]

    return items

def get_table(name):
    if name not in cached_tables:
        meta = MetaData()
        meta.reflect(bind=model.meta.engine)
        table = meta.tables[name]
        cached_tables[name] = table
    return cached_tables[name]