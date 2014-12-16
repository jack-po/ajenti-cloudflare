#!/usr/bin/env python
##
#    CloudFlare API
#         
#    This is a library created to easily interact with CloudFlare's API in Python
#       API Documentation is located at http://www.cloudflare.com/docs/client-api.html
#    
#    @author     David Lasley <[email protected]>
#    @url        https://blog.dlasley.net/random-scripts-2/cloudflare-api-py/
#    @package    toolbox.cloudflare
#    @license    GPLv3 (http://www.gnu.org/licenses/gpl-3.0.html)
#    @version    $Id: cloudflare.py bcfe2db60346 2013-12-13 22:25:47Z dlasley $

__version__ = "$Revision: bcfe2db60346 $"

import json
from urllib2 import urlopen, quote

class CloudFlare(object):
    GATEWAY = 'https://www.cloudflare.com/api_json.html'

    def __init__(self, api_key, email):
        self.tkn = api_key
        self.email = email

    #
    #   ACCESS
    #
    def stats(self, zone, interval):
        '''
            Retrieve the current stats and settings for a particular website.
                This function can be used to get currently settings of values
                such as the security level.
            @param  str zone     The zone (domain) that statistics are being retrieved from
            @param  int interval The time interval for the statistics denoted by these values:
                                    For these values, the latest data is from one day ago
                                        20 = Past 30 days
                                        30 = Past 7 days
                                        40 = Past day
                                        
                                    The values are for Pro accounts
                                        100 = 24 hours ago
                                        110 = 12 hours ago
                                        120 = 6 hours ago
            @return dict
        '''
        return self._do_api_call({'z':zone, 'interval':interval, 'a':'stats'})['result']

    def zone_load_multi(self, ):
        '''
            This lists all domains in a CloudFlare account along with other data.
            @return dict
        '''
        return self._do_api_call({'a':'zone_load_multi'})['zones']

    def rec_load_all(self, zone):
        '''
            Lists all of the DNS records from a particular domain in a CloudFlare account
            @param  str zone    The domain that records are being retrieved from
            @return dict    
        '''
        return self._do_api_call({'a':'rec_load_all', 'z':zone})['recs']

    def zone_check(self, zones):
        '''
            Checks for active zones and returns their corresponding zids
            @param  list    zones   List of zones to check
            @return dict    Name:ID
        '''
        return self._do_api_call({'a':'zone_check', 'zones':','.join(zones)})['zones']

    def zone_ips(self, zone, hours=24, class_=None, geo=False):
        '''
            Returns a list of IP address which hit your site classified by type.
            @param  str     zone    The target domain
            @param  int     hours   Past number of hours to query. Maximum is 48.
            @param  str     class_  Optional. Restrict the result set to a given class as given by:
                                        "r" -- regular
                                        "s" -- crawler
                                        "t" -- threat
            @param  bool    geo     Add longitude and latitude information to response
            @return list    IP list
        '''
        return self._do_api_call({'a':'zone_ips', 'z':zone, 'hours':hours,
                                  'class':class_, 'geo':int(geo)})['ips']

    def ip_lkup(self, ip):
        '''
            Find the current threat score for a given IP.
                Note that scores are on a logarithmic scale,
                where a higher score indicates a higher threat.
            @param  str ip  Target IP
            @return str Lookup result
        '''
        return self._do_api_call({'a':'ip_lkup', 'ip':ip})[ip]

    def zone_settings(self, zone):
        '''
            Retrieves all current settings for a given domain.
            @param  str zone    The target domain
            @return list    result zone objects
        '''
        self._do_api_call({'a':'zone_settings', 'z':zone})['result']['objs']

    #
    #   Modify
    #
    def sec_lvl(self, zone, lvl):
        '''
            This function sets the Basic Security Level to I'M UNDER ATTACK! / HIGH / MEDIUM / LOW / ESSENTIALLY OFF.
            @param  str zone    The domain that records are being retrieved from
            @param  str lvl     The security level:
                                    "help" -- I'm under attack!
                                    "high" -- High
                                    "med" -- Medium
                                    "low" -- Low
                                    "eoff" -- Essentially Off
            @return dict    zone_obj
        '''
        return self._do_api_call({'a':'sec_lvl', 'z':zone, 'v':lvl})['zone']

    def cache_lvl(self, zone, lvl):
        '''
            This function sets the Caching Level to Aggressive or Basic.
            @param  str zone    The target domain
            @param  str lvl     The cache level:
                                    "agg" -- Aggressive
                                    "basic" -- Basic
            @return dict zone_obj
        '''
        return self._do_api_call({'a':'cache_lvl', 'z':zone, 'v':lvl})['zone']['obj']

    def devmode(self, zone, lvl=False):
        '''
            This function allows you to toggle Development Mode on or off for a particular domain.
                When Development Mode is on the cache is bypassed.
                Development mode remains on for 3 hours or until when it is toggled back off.
            @param  str     zone    The target domain
            @param  bool    lvl     True for `on` False for `off`
            @return dict    zone_obj
        '''
        return self._do_api_call({'a':'devmode', 'z':zone, 'v':int(lvl)})['zone']['obj']

    def fpurge_ts(self, zone):
        '''
            This function will purge CloudFlare of any cached files.
                It may take up to 48 hours for the cache to rebuild and
                optimum performance to be achieved.
                This function should be used sparingly.
            @param  str zone    The target domain
            @return dict    zone_obj
        '''
        return self._do_api_call({'a':'fpurge_ts', 'z':zone, 'v':1})['zone']['obj']

    def zone_file_purge(self, zone, url):
        '''
            This function will purge a single file from CloudFlare's cache.
            @param   str zone    The target domain
            @param   str url     The full URL of the file that needs to be purged from Cloudflare's cache.
                                    Keep in mind, that if an HTTP and an HTTPS version of the file exists,
                                    then both versions will need to be purged independently
            @return dict
        '''
        return self._do_api_call({'a':'zone_file_purge', 'z':zone, 'url':url})

    def zone_grab(self, zid):
        '''
            Tells CloudFlare to take a new image of your site.
            @param  int zid ID of zone, found in zone_check
            @return bool
        '''
        return self._do_api_call({'a':'zone_grab', 'zid':zid})

    def ip_to_lists(self, ip, list_='nul'):
        '''
            Add/Remove IP From Whitelist/Blacklist
                and use "nul" to remove the IP from either of those lists
            @param  str ip      The IP Address you want to whitelist/blacklist
            @param  str list_   Which list to modify:
                                    "wl" -- add to whitelist
                                    "ban" -- add to blacklist
                                    "nul" -- remove from all lists
            @return dict
        '''
        return self._do_api_call({'a':list_, 'key':ip})

    def ipv46(self, zone, lvl=False):
        '''
            Toggles IPv6 support
            @param  str     zone    The target domain
            @param  bool    lvl     True to enable
            @return dict    zone_obj
        '''
        return self._do_api_call({'a':'ipv46', 'z':zone, 'v':int(lvl)})['zone']['obj']

    def async(self, zone, lvl):
        '''
            Changes Rocket Loader setting
            @param  str zone    The target domain
            @param  int lvl     Rocket Loader Lvl:
                                    0 -- Off
                                    1 -- Auto
                                    2 -- Manual
            @return bool
        '''
        lvl_map = {0:0, 1:'a', 2:'m'}
        return self._do_api_call({'a':'async', 'z':zone, 'v':lvl_map[lvl]})

    def minify(self, zone, lvl):
        '''
            Changes minification settings
            @param  str zone    The target domain
            @param  int lvl     What to minify:
                                    0 -- off
                                    1 -- JavaScript only
                                    2 -- CSS only
                                    3 -- JavaScript and CSS
                                    4 -- HTML only
                                    5 -- JavaScript and HTML
                                    6 -- CSS and HTML
                                    7 -- CSS, JavaScript, and HTML
            @return bool
        '''
        return self._do_api_call({'a':'minify', 'z':zone, 'v':lvl})

    def mirage2(self, zone, lvl=False):
        '''
            Toggles mirage2 support
            @param  str     zone    The target domain.
            @param  bool    lvl     True for on
            @return bool
        '''
        return self._do_api_call({'a':'mirage2', 'z':zone, 'v':lvl})

    #
    #   Record Management
    #
    def rec_edit(self, zone, type_, name, content, ttl=1, prio=None,
                 service=None, srvname=None, protocol=None, weight=None,
                 port=None, target=None, rec_id=None):
        '''
            Create or Edit a DNS record for a zone
            @param  str zone     The target domain.
            @param  str type_    Type of DNS record. Values include: [A/CNAME/MX/TXT/SPF/AAAA/NS/SRV/LOC]
            @param  str name     Name of the DNS record.
            @param  str content  The content of the DNS record, will depend on the the type of record being added
            @param  int ttl      TTL of record in seconds. 1 = Automatic, otherwise, value must in between 120 and 4,294,967,295 seconds.
            @param  int prio     MX record priority. [applies to MX/SRV]
            @param  str service  Service for SRV record [applies to SRV]
            @param  str srvname  Service Name for SRV record [applies to SRV]
            @param  str protocol Protocol for SRV record. Values include: [_tcp/_udp/_tls]. [applies to SRV]
            @param  int weight   Weight for SRV record. [applies to SRV]
            @param  int port     Port for SRV record. [applies to SRV]
            @param  str target   Target for SRV record. [applies to SRV]
            @param  int rec_id   DNS Record ID. Available by using the rec_load_all call. [`None` for new]
            @return dict    rec_obj
        '''
        #   List of possible values for type_
        type_vals = ['A', 'CNAME', 'MX', 'TXT', 'SPF', 'AAAA',
                     'NS', 'SRC', 'LOC' ]
        if type_ not in type_vals:
            raise LookupError(
                '"%s" is not a valid DNS record type. Valid types are "%s"' % (
                    type_, ','.join(type_vals)
                ))

        #   Check required params
        req_params = {
            'MX':[prio],
            'SRV':[prio, service, srvname, protocol, weight, port, target]
        }
        if None in req_params.get(type_, [True]):
            raise TypeError('Not all parameters were supplied for this record type.')

        data_var = {
            'a':'rec_new', 'z':zone, 'type':type_, 'name':name, 'content':content,
            'ttl':ttl, 'prio':prio, 'service':service, 'srvname':srvname,
            'protocol':protocol, 'weight':weight, 'port':port, 'target':target}

        if rec_id is not None:
            data_var.update({'a':'rec_edit', 'id':rec_id})

        return self._do_api_call(data_var)['rec']['obj']

    def rec_delete(self, zone, rec_id):
        '''
            Delete a record for a domain.
            @param  str zone     The target domain.
            @param  int rec_id   DNS Record ID. Available by using the rec_load_all call.
            @return bool
        '''
        if not isinstance(rec_id, int):
            raise TypeError('rec_id (%s) is of type %s, but should be int' % (
                rec_id, type(rec_id)))

        return self._do_api_call({'a':'rec_delete', 'z':zone, 'id':rec_id})

    def _do_api_call(self, data):
        '''
            URLEncode data with tkn and email appended, then perform API call
            @param  dict    data    POST data
            @return dict
        '''
        #   Add tkn and email for auth
        data['tkn'] = self.tkn
        data['email'] = self.email
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