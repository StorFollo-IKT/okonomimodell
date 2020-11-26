import json

from costs.models import Workstation


class WorkstationsSCCM:
    json = None

    def load_json_file(self, file):
        with open(file, 'r', encoding='utf16') as fp:
            data = json.load(fp)
            self.load(data)

    def load_string(self, customer, string):
        if type(string) == bytes:
            mode = 'wb'
        else:
            mode = 'w'

        file = '/home/datagrunnlag/SCCM/SCCM_%s.json' % customer
        with open(file, mode) as fp:
            fp.write(string)

    def load(self, data):
        for workstation in data:
            try:
                workstation_obj = Workstation.objects.get(serial=workstation['SerialNumber0'])
            except Workstation.DoesNotExist:
                workstation_obj = Workstation(serial=workstation['SerialNumber0'])

            workstation_obj.manufacturer = workstation['Manufacturer0']
            workstation_obj.model = workstation['Model0']
            workstation_obj.name = workstation['Name0']
            workstation_obj.distinguishedName = workstation['Distinguished_Name0']
