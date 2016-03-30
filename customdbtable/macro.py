# -*- coding: utf-8 -*-

from genshi.builder import tag

from trac.core import TracError
from trac.web.chrome import add_stylesheet, Chrome
from trac.wiki.api import parse_args
from trac.wiki.macros import WikiMacroBase

from customdbtable.api import CustomDBTableSystem


class CustomDBTableMacro(WikiMacroBase):
    """A macro to display a table fo CustumDBTable
    {{{
    [[CustomDBTable(<table_name>[,<options>]]]
    }}}

    Available options:
     * `column=` - `|` separated column names
     * `exclude=` - `|` exclude item by 'name' column
    """

    def expand_macro(self, formatter, name, content):
        args, opts = parse_args(content)
        if len(args) != 1:
            raise TracError("Requied single table name")
        table = args[0]
        excludes = [e.strip() for e in opts.get('exclude', '').split('|')]

        cdtsys = CustomDBTableSystem(self.env)
        try:
            columns = cdtsys.column_names(table)
        except:
            raise TracError("Table not found: %s" % table)

        _columns = opts.get('column', '')
        if _columns:
            _columns = [c.strip() for c in _columns.split('|')]
            if len(_columns) == 0:
                raise TracError("No column specified")
            for c in _columns:
                if c not in columns:
                    raise TracError("Column not found: %s" % c)
        else:
            _columns = columns

        ttable = tag.table(class_='wiki customdbtable')
        for row in cdtsys.sorted_dicts(table):
            if row['name'] in excludes:
                continue
            tr = tag.tr()
            for c in _columns:
                tr(tag.td(row[c]))
            ttable(tr)
        return ttable


class CustomDBTableFlatMacro(WikiMacroBase):
    """A macro to display a simple table of CustumDBTable 'name' field.
    {{{
    [[CustomDBTable(<table_name>[,<options>]]]
    }}}

    Available options:
     * `exclude=` - `|` exclude item by 'name' column
     * `column_count=` - The number of column count. (Default: 3)
    """
    def expand_macro(self, formatter, name, content):
        args, opts = parse_args(content)
        if len(args) != 1:
            raise TracError("Requied single table name")
        table = args[0]
        excludes = [e.strip() for e in opts.get('exclude', '').split('|')]
        ccount = int(opts.get('column_count', 3))

        cdtsys = CustomDBTableSystem(self.env)
        try:
            items = cdtsys.sorted_column(table, 'name')
        except:
            raise TracError("Table not found: %s" % table)

        if excludes:
            items = [e for e in items if e not in excludes]

        ttable = tag.table(class_='wiki customdbtable')
        tr = td = None
        i = 0
        for item in items:
            if i % ccount == 0:
                tr = tag.tr()
                ttable(tr)
            td = tag.td(item)
            tr(td)
            i += 1
        while i % ccount != 0:
            tr(tag.td())
            i += 1
        return ttable
