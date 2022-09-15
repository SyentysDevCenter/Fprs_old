from odoo import api, fields, models
from odoo.exceptions import UserError
#
from bs4 import BeautifulSoup

class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def change_image_size(self, html, new_size):
        soup = BeautifulSoup(html, 'html.parser')
        new_width = "width: " + str(new_size) + "%"
        for img in soup.find_all('img'):
            if not 'style' in img.attrs:
                img.attrs['style'] = new_width
            elif 'width' in img.attrs['style']:
                style_list = img.attrs['style'].split(';')
                new_style = ""
                for style in style_list:
                    style = style.strip()
                    if 'width' in style:
                        style = new_width
                    if "" != style:
                        new_style = new_style + style + ";"
                img.attrs['style'] = new_style
            else:
                img.attrs['style'] = img.attrs['style'] + new_width
        return soup



    def print_img_small_size(self):
        for task in self:
            task.description = task.change_image_size(task.description, 35)

   #  @api.model
   #  def write(self, values):
   #      if 'description' in values:
   #          new_html = self.change_image_size(values['description'], 20)
   #          values['description'] = new_html
    #     return super(ProjectTask, self).write(values)

   #  @api.model
   #  def create(self, values):
   #      if 'description' in values:
   #          new_html = self.change_image_size(values['description'], 20)
   #          values['description'] = new_html
    #     return super(ProjectTask, self).create(values)


    # @api.model
    # def write(self, values):
    #     if 'description' in values:
    #         new_html = self.change_image_size(values['description'], 20)
    #         values['description'] = new_html
    #     return super(ProjectTask, self).write(values)
    #
    # @api.model
    # def create(self, values):
    #     if 'description' in values:
    #         new_html = self.change_image_size(values['description'], 20)
    #         values['description'] = new_html
    #     return super(ProjectTask, self).create(values)
