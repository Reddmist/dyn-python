# -*- coding: utf-8 -*-
from ..utils import Active
from ..session import DynectSession, DNSAPIObject
from ...core import (APIService, StringAttribute, ImmutableAttribute,
                     ListAttribute, ValidatedListAttribute, IntegerAttribute)
from ...compat import force_unicode

__author__ = 'jnappi'
__all__ = ['ReverseDNS']


class ReverseDNS(APIService, DNSAPIObject):
    """A DynECT ReverseDNS service"""
    uri = '/IPTrack/{zone}/{fqdn}/'
    _get_length = 1

    zone = ImmutableAttribute('zone')
    fqdn = ImmutableAttribute('fqdn')
    hosts = ListAttribute('hosts')
    netmask = StringAttribute('netmask')
    ttl = IntegerAttribute('ttl')
    record_types = ValidatedListAttribute('record_types',
                                          validator=('A', 'AAAA', 'DynA',
                                                     'DynAAAA'))
    iptrack_id = StringAttribute('iptrack_id')

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an new :class:`ReverseDNS` object instance

        :param zone: The zone under which this service will be attached
        :param fqdn: The fqdn where this service will be located
        :param hosts: A list of Hostnames of the zones where you want to track
            records
        :param netmask: A netmask to match A/AAAA rdata against. Matched
            records will get PTR records, any others won't
        :param ttl: TTL for the created PTR records. May be omitted, explicitly
            specified, set to 'default', or 'match'
        :param record_types: A list of which type of records this service will
            track. Note: Both A and AAAA can not be monitored by the same
            service
        """
        self.uri = self.uri.format(zone=zone, fqdn=fqdn)
        super(ReverseDNS, self).__init__(*args, **kwargs)

    def _post(self, hosts, netmask, ttl='default', record_types=None):
        """Create a new ReverseDNS Service on the DynECT System"""
        record_types = ['A'] if record_types is None else record_types
        self.record_types = record_types  # Validation check
        api_args = {'record_types': self.record_types, 'hosts': hosts,
                    'netmask': netmask}
        if ttl is not None:
            api_args['ttl'] = ttl
        response = DynectSession.post(self.uri, api_args)
        self._build(response['data'])

    def _get(self, service_id):
        """Build an object around an existing DynECT ReverseDNS Service"""
        uri = '/IPTrack/{0}/{1}/{2}/'.format(self.zone, self.fqdn, service_id)
        response = DynectSession.get(uri)
        self._build(response['data'])

    def _build(self, data):
        """Build this object based on the data contained in an API response"""
        if 'active' in data:
            self._active = Active(data.pop('active'))
        super(ReverseDNS, self)._build(data)
        self.uri += '{0}/'.format(self.iptrack_id)

    def _update(self, **api_args):
        special_cases = 'record_types', 'hosts', 'ttl', 'netmask'
        for key in api_args:
            if key in special_cases:
                api_args['record_types'] = self.record_types
                api_args['hosts'] = self.hosts
                break  # Only need to check/assign them once
        super(ReverseDNS, self)._update(**api_args)

    def __str__(self):
        return force_unicode('<ReverseDNS>: {0}').format(self.fqdn)
