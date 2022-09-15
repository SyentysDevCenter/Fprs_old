from odoo import api, fields, models

class Ao(models.Model):
    _inherit = 'ao.ao'

    lot_ids = fields.One2many('ao.lot', 'ao_id', 'Lots')
    lot_count = fields.Integer('#Lots', compute='compute_lot_count', store=True)



    @api.depends('lot_ids')
    def compute_lot_count(self):
        for rec in self:
            rec.lot_count = len(rec.lot_ids)


    def action_open_ao_lot(self):
        self.ensure_one()

        action = {
            'name': 'Lots',
            'type': 'ir.actions.act_window',
            'res_model': 'ao.lot',
            'view_mode': 'tree,form',
            'context': {'default_ao_id': self.id,
                        },
            'domain': [('ao_id', '=', self.id)],
            'target': 'current',
        }
        return action

    def action_open_project_wbs(self):
        action = super(Ao, self).action_open_project_wbs()
        action['context']['search_default_group_by_lot'] = 1
        return action

    def action_open_gantt(self):
        self.ensure_one()
        wbs_ids = [wbs.id for wbs in self.project_id.wbs_ids]


        return {
            'name': 'Gantt chart',
            'type': 'ir.actions.act_window',
            'res_model': 'project.wbs',
            'view_mode': 'gantt',
            'target': 'current',
            'context': {'default_project_id': self.project_id.id, 'project_id': self.project_id.id},
            'domain': [("id", "in", wbs_ids)],
        }


class AoLot(models.Model):
    _name = 'ao.lot'

    ao_id = fields.Many2one('ao.ao', 'Ao', required=True)
    name = fields.Char('Intitulé', required=True)
    user_id = fields.Many2one('res.partner', "Chargé d'affaire")
    conducteur_travaux_id = fields.Many2one('res.users', 'Conducteur des travaux')
    state = fields.Selection([('new','Nouveau'), ('gagne', 'Gagné'), ('perdu', 'Perdu')], default='new')
    motif_rejet = fields.Text('Motif de rejet')
    wbs_ids = fields.One2many('project.wbs', 'lot_id', 'BDP')
    wbs_count = fields.Integer(compute='compute_wbs_count', store=True, string='# BDP')

    def action_gagner(self):
        self.write({'state': 'gagne'})

    def action_perdu(self):
        self.write({'state': 'perdu'})
    @api.depends('wbs_ids')
    def compute_wbs_count(self):
        for rec in self:
            rec.wbs_count = len(rec.wbs_ids)

    def action_open_gantt(self):
        self.ensure_one()
        if self.ao_id.project_id:

            return {
                'name': 'Gantt chart',
                'type': 'ir.actions.act_window',
                'res_model': 'project.wbs',
                'view_mode': 'gantt',
                'target': 'current',
                'context': {'default_project_id': self.ao_id.project_id.id, 'project_id': self.ao_id.project_id.id},
                'domain': [("id", "in", self.wbs_ids.mapped('id'))],
            }

    def action_open_lot_wbs(self):
        self.ensure_one()
        if not self.ao_id.project_id:
            project_obj = self.env['project.project']
            project_id = project_obj.create(
                {
                    'name': self.ao_id.name,
                    'active': False,
                }
            )
            self.ao_id.project_id = project_id

        action = {
            'name': 'BDP',
            'type': 'ir.actions.act_window',
            'res_model': 'project.wbs',
            'view_mode': 'tree,form',
            'context': {'default_lot_id': self.id,
                        'default_ao_id': self.ao_id.id,
                        'default_project_id': self.ao_id.project_id.id,

                        },
            'domain': [('lot_id', '=', self.id)],
            'target': 'current',
        }
        return action


class ProjectWbs(models.Model):
    _inherit = 'project.wbs'

    lot_id = fields.Many2one('ao.lot')


