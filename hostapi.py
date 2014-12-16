#!/usr/bin/env python

import json
from urllib2 import urlopen, quote

class CloudFlareHostAPI(object):
    GATEWAY = 'https://api.cloudflare.com/host-gw.html'

    def __init__(self, host_key):
        self.host_key = host_key

    def user_create(self, email, password, unique_id=None):
        '''
            Create a CloudFlare account mapped to your user.
            @param  str     email       The User's e-mail address for the new CloudFlare account.
            @param  str     password    The User's password for the new CloudFlare account. CloudFlare will never store this password in clear text.
            @param  str     unique_id   Optional. Set a unique string identifying the User.
            @return bool
        '''
        return self._do_api_call({'act':'user_create', 'cloudflare_email':email, 'cloudflare_pass':password,
                                  'unique_id':unique_id})

    def user_auth(self, email, password, unique_id=None):
        '''
            Authorize access to a user's existing CloudFlare account.
            @param  str     email       The User's e-mail address for the new CloudFlare account.
            @param  str     password    The User's password for the new CloudFlare account. CloudFlare will never store this password in clear text.
            @param  str     unique_id   Optional. Set a unique string identifying the User.
            @return bool
        '''
        return self._do_api_call({'act':'user_auth', 'cloudflare_email':email, 'cloudflare_pass':password,
                                  'unique_id':unique_id})

    def zone_set(self, user_key, zone_name, resolve_to, subdomains):
        '''
            Setup a User's zone for CNAME hosting..
            @param  str     user_key    The unique 32 hex character auth string, identifying the user's CloudFlare Account.
            @param  str     zone_name   The zone you'd like to run CNAMES through CloudFlare for, e.g. "example.com".
            @param  str     resolve_to  The CNAME that CloudFlare should ultimately resolve web connections to after they have been filtered, e.g. "resolve-to-cloudflare.example.com".
            @param  str     subdomains  A comma-separated string of subdomain(s) that CloudFlare should host, e.g. "www,blog,forums" or "www.example.com,blog.example.com,forums.example.com".
            @return bool
        '''
        return self._do_api_call({'act':'zone_set', 'user_key':user_key, 'zone_name':zone_name,
                                  'resolve_to':resolve_to, 'subdomains':subdomains})

    def zone_delete(self, user_key, zone_name):
        '''
            Delete a specific zone on behalf of a user
            @param  str     user_key    The unique 32 hex character auth string, identifying the user's CloudFlare Account.
            @param  str     zone_name   The zone you'd like to lookup, e.g. "example.com".
            @return bool
        '''
        return self._do_api_call({'act':'zone_delete', 'user_key':user_key, 'zone_name':zone_name})

    def _do_api_call(self, data):
        '''
            URLEncode data with host_key appended, then perform API call
            @param  dict    data    POST data
            @return dict
        '''
        #   Add tkn and email for auth
        data['host_key'] = self.host_key
        #   URLEscape
        out = []
        for key, val in data.iteritems():
            if val:
                out.append('%s=%s' % (quote(key), quote(str(val))))
        data = '&'.join(out)
        #   Send and parse
        response = json.loads(urlopen(self.GATEWAY, data).read())
        if response['result'] == 'success':
            return response.get('response', True)
        else:
            raise EnvironmentError('Invalid response received\r\n%r' % response)