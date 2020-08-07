from pprint import pprint

import ldap
from ldap.controls import SimplePagedResultsControl

from adimport.ad.paginated_lookup import paginated_query

response_types = {
    0: 'success',
    1: 'operationsError',
    2: 'protocolError',
    3: 'timeLimitExceeded',
    4: 'sizeLimitExceeded',
    5: 'compareFalse',
    6: 'compareTrue',
    7: 'authMethodNotSupported',
    8: 'strongerAuthRequired',
    10: 'referral',
    11: 'adminLimitExceeded',
    12: 'unavailableCriticalExtension',
    13: 'confidentialityRequired',
    14: 'saslBindInProgress',
    16: 'noSuchAttribute',
    17: 'undefinedAttributeType',
    18: 'inappropriateMatching',
    19: 'constraintViolation',
    20: 'attributeOrValueExists',
    21: 'invalidAttributeSyntax',
    32: 'noSuchObject',
    33: 'aliasProblem',
    34: 'invalidDNSyntax',
    35: 'isLeaf',
    36: 'aliasDereferencingProblem',
    48: 'inappropriateAuthentication',
    49: 'invalidCredentials',
    50: 'insufficientAccessRights',
    51: 'busy',
    52: 'unavailable',
    53: 'unwillingToPerform',
    54: 'loopDetect',
    60: 'sortControlMissing',
    61: 'offsetRangeError',
    64: 'namingViolation',
    65: 'objectClassViolation',
    66: 'notAllowedOnNonLeaf',
    67: 'notAllowedOnRDN',
    68: 'entryAlreadyExists',
    69: 'objectClassModsProhibited',
    70: 'resultsTooLarge',
    71: 'affectsMultipleDSAs',
    76: 'virtualListViewError or controlError',
    80: 'other',
    81: 'serverDown',
    82: 'localError',
    83: 'encodingError',
    84: 'decodingError',
    85: 'timeout',
    86: 'authUnknown',
    87: 'filterError',
    88: 'userCanceled',
    89: 'paramError',
    90: 'noMemory',
    91: 'connectError',
    92: 'notSupported',
    93: 'controlNotFound',
    94: 'noResultsReturned',
    95: 'moreResultsToReturn',
    96: 'clientLoop',
    97: 'referralLimitExceeded',
    100: 'invalidResponse',
    101: 'ambiguousResponse',
    112: 'tlsNotSupported',
    113: 'intermediateResponse',
    114: 'unknownType',
    118: 'canceled',
    119: 'noSuchOperation',
    120: 'tooLate',
    121: 'cannotCancel',
    122: 'assertionFailed',
    123: 'authorizationDenied',
    4096: 'e-syncRefreshRequired',
    16654: 'noOperation',
}


class ActiveDirectory:
    ldap = None
    base_dn = None

    def __init__(self):
        self.page_control = SimplePagedResultsControl(True, size=1000, cookie='')

    def connect(self, dc, username, password, base_dn=None, ldaps=False, port=None):
        if ldaps:
            protocol = 'ldaps'
        else:
            protocol = 'ldap'

        if protocol == 'ldaps' and port is None:
            port = 636
        else:
            port = 389

        self.base_dn = base_dn

        ldap.set_option(ldap.OPT_REFERRALS, 0)
        ldap.set_option(ldap.OPT_NETWORK_TIMEOUT, 2)
        ldap.set_option(ldap.OPT_SIZELIMIT, 2500)

        self.ldap = ldap.initialize('%s://%s:%d' % (protocol, dc, port), bytes_mode=False)
        self.ldap.simple_bind_s(username, password)

    def ldap_query(self, query, base_dn, single_result=True, subtree=True, attributes=None, pagination=False):
        if attributes is None:
            attributes = ['dn']
        if subtree:
            scope = ldap.SCOPE_SUBTREE
        else:
            scope = ldap.SCOPE_ONELEVEL

        if not pagination:
            entries = self.ldap.search_s(base_dn, scope, query, attributes)
        else:
            return paginated_query(self.ldap, attributes, base_dn, scope, query)

        """if len(attributes) == 1:
            return entries[1]"""

        return entries

    def group_members(self, group_dn):
        members = self.ldap_query('(distinguishedName=%s)' % group_dn, attributes=['member'],
                                  single_result=False, base_dn=self.base_dn)
        return members[0][1]['member']

    def organizational_units(self, base_dn=None, subtree=True):
        if not base_dn:
            base_dn = self.base_dn
        return self.ldap_query('(objectClass=organizationalUnit)', base_dn, single_result=False, subtree=subtree)
