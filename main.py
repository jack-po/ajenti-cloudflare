from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from backend import CloudFlareBackend

class Record (object):
    def __init__(self, type, name, content, rec_id = None, ttl = 1, prio = None):
        self.id = rec_id
        self.type = type
        self.name = name
        self.content = content
        self.ttl = int(ttl) if ttl else None
        self.prio = int(prio) if prio else None
        self._saved_hash = self.hash()

    def hash(self):
        return hash((self.id, self.type, self.name, self.content, self.ttl, self.prio))

class Zone (object):
    def __init__(self, name = '', resolve_to = '', subdomains = ''):
        self.name = name
        self.resolve_to = resolve_to
        self.subdomains = subdomains

@plugin
class CloudFlare (SectionPlugin):
    def init(self):
        self.title = _('CloudFlare')
        self.icon = 'cloud'
        self.category = _('Web')

        self.append(self.ui.inflate('cloudflare:main'))
        self.find('type-box').labels = ['A', 'CNAME', 'MX', 'TXT', 'SPF', 'AAAA', 'NS', 'LOC']
        self.find('type-box').values = ['A', 'CNAME', 'MX', 'TXT', 'SPF', 'AAAA', 'NS', 'LOC']
        self.find('records').new_item = lambda c: Record(type = 'A', name='', content='', ttl=1)
        self.find('records').delete_item = self.delete

        self.zone_new = {}
        self.current_zone = None

        self.backend = CloudFlareBackend.get()
        self.binder_config = Binder(self.backend, self.find('config'))
        self.binder = Binder(None, self)

        def post_zone_del_bind(object, collection, item, ui):
            ui.find('zone-delete').on('click', self.on_zone_delete, item)

        self.find('zones-setup').find('zones-list').post_item_bind = post_zone_del_bind

    def on_page_load(self):
        self.refresh()
        pass

    @on('zone-select', 'click')
    def on_zone_select(self):
        self.current_zone = self.find('zones').value
        self.refresh()

    @on('zone-add', 'click')
    def on_zone_add(self):
        self.binder.update()

        try:
            self.backend.zone_add(self.zone_new['name'], self.zone_new['resolve_to'], self.zone_new['subdomains'])
            self.zone_new = {}
        except Exception, e:
            self.context.notify('error', e.message)

        self.refresh()

    def on_zone_delete(self, zone):
        try:
            self.backend.zone_delete(zone.name)
            self.refresh()
        except Exception, e:
            self.context.notify('error', e.message)


    def delete(self, i, collection):
        self.deleted_records.append(i)
        collection.remove(i)

    @on('save', 'click')
    def save(self):
        self.binder.update()

        for record in self.records:
            # new records
            if record.id is None:
                try:
                    self.backend.rec_edit(self.current_zone, record.type, record.name, record.content, record.ttl, record.prio)
                except Exception, e:
                    self.context.notify('error', e.message)
                continue

            # changed records
            if record._saved_hash != record.hash():
                try:
                    self.backend.rec_edit(self.current_zone, record.type, record.name, record.content, record.ttl, record.prio, rec_id=int(record.id))
                except Exception, e:
                    self.context.notify('error', e.message)

        for record in self.deleted_records:
            # deleted records
            try:
                self.backend.rec_delete(self.current_zone, rec_id=int(record.id))
            except Exception, e:
                self.context.notify('error', e.message)

        self.refresh()

    @on('zone-refresh', 'click')
    def refresh(self):
        self.binder_config.populate()

        try:
            self.backend.setup()
        except Exception, e:
            self.context.notify('error', _('CloudFlare authentication failed'))
            self.find_type('tabs').active = 2
            # self.context.launch('configure-plugin', plugin=self.backend)
            return

        zones_select = self.find('records-config').find('zones')

        try:
            zones_json = self.backend.get_zones()

            if not zones_json.has_key('objs'):
                return

            zones = [x['zone_name'] for x in zones_json['objs']]
            zones_select.values = zones_select.labels = zones
            self.zones = [Zone(name = x) for x in zones]

            if self.current_zone is not None:
                zones_select.value = self.current_zone
            else:
                self.current_zone = zones_select.value

            records_json = self.backend.get_records(zones_select.value)

            self.records = [Record(x['type'], x['name'], x['content'], x['rec_id'], ttl=x['ttl'], prio=x['prio']) for x in records_json['objs']]
            self.deleted_records = []

            self.binder.setup(self).populate()
        except Exception, e:
            self.context.notify('error', e.message)

    @on('save-config', 'click')
    def save_config(self):
        self.binder_config.update()

        if self.backend.save_classconfig():
            self.find_type('tabs').active = 0

        self.refresh()

