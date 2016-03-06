# encoding: utf-8

from pkg_resources import resource_filename

from genshi.core import Markup
from genshi.builder import tag
from genshi.filters.transform import Transformer

from trac.core import Component, implements
from trac.util.compat import *

from trac.admin.api import IAdminPanelProvider
from trac.web.chrome import ITemplateProvider

from customdbtable.api import CustomDBTableSystem


class CustomDBTableAdminPanel (Component):
    implements(ITemplateProvider, IAdminPanelProvider)

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        return []
        #yield 'customdbtable', resource_filename(__name__, 'htdocs')

    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]


    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        for name, info in CustomDBTableSystem(self.env)._dbs.items():
            yield('customdbtable', 'Custom Tables',
                    name, info['label'])

    def render_admin_panel(self, req, cat, page, item):
        if req.method == 'POST':
            dbsys = CustomDBTableSystem(self.env)
            if item:
                if not req.args.get('cancel'):
                    dbsys.update(page, req.args)

            if req.args.get('add'):
                dbsys.add(page, req.args)
            elif req.args.get('remove'):
                sel = req.args.get('sel')
                sels = isinstance(sel, list) and sel or [sel]
                if not sel:
                    raise TracError, 'Nothing selected'
                for name in sels:
                    dbsys.remove(page, name)

        # Render
        if item:
            return self._render_table_item(req, page, item)
        return self._render_table_list(req, page)


    def _render_table_list (self, req, page):
        cdtsys = CustomDBTableSystem(self.env)
        dbinfo = cdtsys._dbs[page]
        data = {
            'table_name': page,
            'table_label': dbinfo['label'],
            'columns': dbinfo['columns'],
            'rows': cdtsys.sorted_items(page),
        }
        return ('admin_list.html', data)

    def _render_table_item (self, req, page, row):
        cdtsys = CustomDBTableSystem(self.env)
        dbinfo = cdtsys._dbs[page]
        data = {
            'table_name': page,
            'table_label': dbinfo['label'],
            'columns': dbinfo['columns'],
            'row': cdtsys.item(page, row),
        }
        return ('admin_item.html', data)
