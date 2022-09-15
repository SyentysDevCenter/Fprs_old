from odoo import api, fields, models
from odoo.exceptions import UserError


class Project(models.Model):
    _inherit = 'project.project'

    prefix = fields.Char(string="Préfixe", required=False, copy=False)

    @api.constrains('name', 'is_rehabilitation')
    def _check_company_id(self):
        for record in self:
            if record.name and record.is_rehabilitation:
                others = self.env['project.project'].search([('name', '=', record.name)])
                if len(others)>1:
                    raise UserError(
                        ('Un autre chantier de réhabilitation est créé avec le nom %s.')%(record.name))

    @api.model
    def create(self, values):
        project = super(Project, self).create(values)

        if project.is_rehabilitation:
            if not project.prefix:
                raise UserError(f'il faut saisir le Préfixe du projet !')
            seq = self.env['ir.sequence'].search([('code', '=', 'code.chantier.sequence')], limit=1)
            # seq = self.env['ir.sequence'].next_by_code('code.chantier.sequence')
            name = project.prefix + str(seq).zfill(seq.padding)
            exist_project = self.env['project.project'].search([('name', '=', name), ('is_rehabilitation', '=', True)])
            if exist_project:
                raise UserError(f'Le nom de projet {name}  exist déjà !')
            project.name = project.prefix + self.env['ir.sequence'].next_by_code('code.chantier.sequence')

        return project
