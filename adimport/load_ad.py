from datetime import datetime

from _ldap import LDAPError

from adimport.ad.ad import ActiveDirectory
from adimport.models import Query
from costs.ad_utils import microsoft_timestamp_to_unix
from costs.models import Customer


class AdLoad:
    def __init__(self, query):
        self.query = query

        self.ad = ActiveDirectory()
        self.ad.connect(query.directory.dc,
                        query.directory.username,
                        query.directory.password,
                        query.directory.dn,
                        query.directory.ldaps)

        if query.base_dn:
            self.base_dn = query.base_dn
        else:
            self.base_dn = query.directory.dn

    @staticmethod
    def run_queries(customer, target, model):
        if customer == 'all':
            customers = Customer.objects.all()
        else:
            customers = Customer.objects.filter(id=customer)

        for customer in customers:
            print(customer)
            queries = Query.objects.filter(directory__customer=customer, target=target)
            if not queries:
                print('No queries for customer %s with target %s' % (customer, target))
                continue

            for query in queries:
                try:
                    ad = AdLoad(query)
                    if query.type == 'computer':
                        ad.load_computers(model)
                except LDAPError as e:
                    print(
                        'Error running query %s on directory %s: %s'
                        % (query.query, query.directory, e.args[0]['desc'])
                    )
                    return

            deleted = model.objects.filter(
                customer=customer,
                last_update__date__lt=datetime.today().date(),
                imported=True,
            )
            deleted.delete()

    def load_computers(self, model):
        attributes = ['distinguishedName', 'dNSHostName', 'lastLogon', 'cn', 'description',
                      'operatingSystem', 'operatingSystemVersion', 'userAccountControl']

        entries = self.ad.ldap_query(self.query.query, self.base_dn, False, True, attributes, True)
        for computer in entries:
            if computer[0] is None:
                continue
            computer = computer[1]

            flag = int(computer['userAccountControl'][0])

            if flag & 2 == 2:  # Check if account is disabled
                continue

            try:
                timestamp = microsoft_timestamp_to_unix(int(computer['lastLogon'][0]))
                last_logon = datetime.fromtimestamp(timestamp)
            except KeyError:
                last_logon = None
            except ValueError:
                last_logon = None

            try:
                computer_obj = model.objects.get(customer=self.query.directory.customer,
                                                 name=computer['cn'][0].decode('utf-8'))
            except model.DoesNotExist:
                computer_obj = model(customer=self.query.directory.customer)

            computer_obj.name = computer['cn'][0].decode('utf-8')
            computer_obj.dn = computer['distinguishedName'][0].decode('utf-8')
            computer_obj.last_logon = last_logon
            computer_obj.dns_name = computer['dNSHostName'][0].decode('utf-8')
            computer_obj.imported = True
            computer_obj.save()
