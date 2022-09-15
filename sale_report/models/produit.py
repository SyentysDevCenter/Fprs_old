from odoo import api, fields, models, _


class Product(models.Model):
    _inherit='product.product'

    def get_designation(self):
            print(self.name)
            if '[' in self.name:
                print(self.name[:self.name.find('[')])
            return self.name[:self.name.find('[')]

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def get_designation(self):

        for x in self.name:
            print(x)
            #
            # if self.name[x] == "[":
            #     return self.name[:x]
        return
