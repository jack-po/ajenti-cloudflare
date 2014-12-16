# coding=utf-8
from ajenti.api import plugin, BasePlugin
from ajenti.plugins.configurator.api import ClassConfigEditor
from api import CloudFlare
from hostapi import CloudFlareHostAPI
import settings

@plugin
class CloudFlareClassConfigEditor (ClassConfigEditor):
    title = 'CloudFlare'
    icon = 'cloud'

    def init(self):
        self.append(self.ui.inflate('cloudflare:config'))


@plugin
class CloudFlareBackend (BasePlugin):
    default_classconfig = {'email': '', 'password': ''}
    classconfig_editor = CloudFlareClassConfigEditor
    host_key = settings.host_key

    def setup(self):
        """
        Initializes instance variables, creates manager instance and tests connection
        @return: Nothing
        """
        # Retrieve configuration settings
        user_key = self.classconfig['user_key']
        user_api_key = self.classconfig['user_api_key']
        email = self.classconfig['email']

        if not user_key:
            raise Exception('No user key specified')

        if not user_api_key:
            raise Exception('No token specified')

        if not email:
            raise Exception('No user api key specified')

    def save_classconfig(self):
        try:
            try:
                json = self.auth(self.classconfig['email'], self.classconfig['password'])
            except EnvironmentError, e:
                json = self.register(self.classconfig['email'], self.classconfig['password'])

            self.classconfig = {'user_key': json['user_key'], 'user_api_key': json['user_api_key'], 'email': self.classconfig['email']}
        except Exception, e:
            self.context.notify('error', e.message)
            return False

        super(CloudFlareBackend, self).save_classconfig()
        return True

    def client_api(self):
        user_key = self.classconfig['user_api_key']
        email = self.classconfig['email']

        return CloudFlare(user_key, email)

    def host_api(self):
        return CloudFlareHostAPI(self.host_key)

    def get_zones(self):
        return self.client_api().zone_load_multi()

    def get_records(self, zone_name):
        return self.client_api().rec_load_all(zone_name)

    def rec_edit(self, zone, type_, name, content, ttl=1, prio=None, rec_id=None):
        return self.client_api().rec_edit(zone, type_, name, content, ttl, prio, rec_id=rec_id)

    def rec_delete(self, zone, rec_id):
        return self.client_api().rec_delete(zone, rec_id)

    def auth(self, email, password):
        return self.host_api().user_auth(email, password)

    def register(self, email, password):
        return self.host_api().user_create(email, password)

    def zone_add(self, zone_name, resolve_to, subdomains):
        return self.host_api().zone_set(self.classconfig['user_key'], zone_name, resolve_to, subdomains)

    def zone_delete(self, zone_name):
        return self.host_api().zone_delete(self.classconfig['user_key'], zone_name)