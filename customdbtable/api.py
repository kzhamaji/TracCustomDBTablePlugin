# encoding: utf-8

from trac.core import Component, implements
from trac.env import IEnvironmentSetupParticipant
from trac.perm import IPermissionRequestor

from trac.util.compat import *
from trac.cache import cached

__all__ = ('CustomDBTableSystem',)

def get_sorted_dicts (env, table, other_env=None):
    if other_env:
        from trac.env import open_environment
        env_path = os.path.join(os.path.dirname(env.path), 'ncs')
        env = open_environment(env_path, use_cache=True)

    return CustomDBTableSystem(env).sorted_dicts(table)


class CustomDBTableSystem (Component):

    implements(IEnvironmentSetupParticipant, IPermissionRequestor)

    # IPermissionRequestor methods
    def get_permission_actions(self):
        return ('CUSTOMDBTABLE_ADMIN',)

    # IEnvironmentSetupParticipant methods
    def environment_created(self):
        pass
    def environment_needs_upgrade(self, db):
        self._dbs
        return False
        tables = db.execute("SELECT name from SQLite_Master").fetchall()
        should_be = set([table[0] for table in self.TABLES])
        return not should_be.issubset(set([row[0] for row in tables]))
    def upgrade_environment(self, db):
        tables = db.execute("SELECT name from SQLite_Master").fetchall()
        cursor = db.cursor()

        for table in self.TABLES:
            name = table[0]
            schema = table[2]
            if name not in [t[0] for t in tables]:
                cursor.execute("CREATE TABLE %s (name text, %s)" %
                    (name,
                     ", ".join([s+" text" for s in schema.split(',')]))
                )

    @cached
    def _dbs (self):
        dbs = {}
        section = self.env.config['custom-db-table']

        by_tables = groupby(section, key=lambda x: x.split('.', 1)[0])
        for name, keys in by_tables:
            db = dbs.setdefault(name, {})
            cols = section.getlist(name)

            db['label'] = section.get(name + '.label', name)
            db['project'] = section.get(name + '.project')
            db['columns'] = columns = []

            for col in cols:
                colinfo = {
                    'name': col,
                    'label': section.get(name+'.'+col+'.label', col)
                }
                columns.append(colinfo)

        return dbs

    def sorted_items (self, table):
        dbinfo = self._dbs[table]
        colinfo = dbinfo['columns']
        with self.env.db_query as db:
            cursor = db.cursor()
            sql = "SELECT %s FROM %s ORDER BY %s" % (
                    ','.join([c['name'] for c in colinfo]),
                    table,
                    colinfo[0]['name'])
            return cursor.execute(sql).fetchall()

    def sorted_dicts (self, table):
        dbinfo = self._dbs[table]
        colinfo = dbinfo['columns']
        dicts = []
        for row in self.sorted_items(table):
            d = {}
            for ci,val in zip(colinfo, row):
                d[ci['name']] = val
            dicts.append(d)
        return dicts

    def item (self, table, name):
        dbinfo = self._dbs[table]
        colinfo = dbinfo['columns']
        with self.env.db_query as db:
            cursor = db.cursor()
            sql = "SELECT %s FROM %s WHERE %s = '%s'" % (
                    ','.join([c['name'] for c in colinfo]),
                    table,
                    colinfo[0]['name'],
                    name)
            return cursor.execute(sql).fetchall()[0]

    def sorted_column (self, table, col):
        dbinfo = self._dbs[table]
        colinfo = dbinfo['columns']
        with self.env.db_query as db:
            cursor = db.cursor()
            sql = "SELECT %s FROM %s ORDER BY %s" % (col, table, col)
            return [r[0] for r in cursor.execute(sql).fetchall()]

    def update (self, table, kws):
        dbinfo = self._dbs[table]
        colinfo = dbinfo['columns']
        pcol = colinfo[0]['name']
        with self.env.db_transaction as db:
            cursor = db.cursor()
            sql = "UPDATE %s SET %s WHERE %s = '%s'" % (
                    table,
                    ','.join(["%s='%s'" % (c['name'], kws.get(c['name'], ''))
                                for c in colinfo[1:]]),
                    pcol, kws.get(pcol))
            cursor.execute(sql)

    def add (self, table, kws):
        dbinfo = self._dbs[table]
        colinfo = dbinfo['columns']
        with self.env.db_transaction as db:
            cursor = db.cursor()
            sql = "INSERT INTO %s VALUES(%s)" % (
                    table,
                    ','.join(["'%s'" % kws.get(c['name'],'') for c in colinfo]),
                    )
            cursor.execute(sql)

    def remove (self, table, name):
        dbinfo = self._dbs[table]
        colinfo = dbinfo['columns']
        with self.env.db_transaction as db:
            cursor = db.cursor()
            sql = "DELETE FROM %s where %s='%s'" % (
                    table,
                    colinfo[0]['name'],
                    name)
            cursor.execute(sql)
