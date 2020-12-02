class InvoiceUtils:
    @staticmethod
    def tax_code(company, percent=25):
        if company == 'AK':
            if percent == 0:
                return '0'
            elif percent == 25:
                return '06'
            else:
                raise AttributeError('Invalid tax amount')
        elif company == 'FK':
            if percent == 0:
                return '0'
            elif percent == 25:
                return '2A'
            elif percent == 15:
                return '2B'
            elif percent == 12:
                return '2C'
            else:
                raise AttributeError('Invalid tax amount')
