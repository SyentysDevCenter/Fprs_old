# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
from datetime import datetime, timedelta


class ProjectWbs(models.Model):
    _name = 'project.wbs'
    _description = 'WBS'
    _inherit = ['mail.thread', 'portal.mixin', 'mail.activity.mixin']
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order = 'code'

    @api.constrains('start_date', 'finish_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.parent_id and record.parent_id.start_date:
                if record.start_date < record.parent_id.start_date:
                    raise ValidationError(
                        u'Date début du WBS  %s doit être entre date début et fin du wbs parent ' % record.name)
                        # u'WBS Start date should between WBS parent start and finish dates for WBS %s' % record.name)
                if record.finish_date and record.parent_id and record.parent_id.finish_date:
                    if record.finish_date > record.parent_id.finish_date:
                        raise ValidationError(
                        u'Date fin du WBS  %s doit être entre date début et fin du wbs parent ' % record.name)

                        # u'WBS Finish date should between WBS parent start and finish dates for WBS %s' % record.name)


    def get_tasks(self):
        self.ensure_one()
        task_ids = [task.id for task in self.task_ids]
        return {
            'name': 'Tasks',
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_type': 'form',
            'view_mode': 'tree,form,kanban,calendar,graph,pivot',
            'domain': [("id", "in", task_ids)],
            'context': {'default_project_id': self.project_id.id,'default_wbs_id': self.id},
            'target': 'current',
        }

    parent_id = fields.Many2one('project.wbs', string='Parent', index=True)
    child_ids = fields.One2many('project.wbs', 'parent_id', 'Childs')
    has_childs = fields.Boolean(u'Has childs', compute="get_has_childs")
    parent_path = fields.Char(index=True)

    name = fields.Char("Nom", required=True)
    code = fields.Char(u"Code WBS", required=True)
    code_client = fields.Char("Code Client", required=True)
    is_milestone = fields.Boolean(u"Jalon")
    is_milestone_complete = fields.Boolean(u"Jalon Complet")
    is_invoicable = fields.Boolean(u"Facturable?", required=True)
    project_id = fields.Many2one('project.project', u"Projet", required=True)
    task_ids = fields.One2many('project.task', 'wbs_id', u"Tâches")
    start_date = fields.Date(u"Date début")
    finish_date = fields.Date(u"Date fin")

    order = fields.Float(u"Ordre")

    duration = fields.Float(u"Durée (jours)", compute='_get_duration', store=True)
    manuel_duration = fields.Float(u"Durée manuelle (jours)")

    cost = fields.Float(u"Coût", compute='_get_cost')
    budget = fields.Float(u"Budget", compute='_get_cost')
    weight = fields.Float(u"Poids", default=1)
    completion_rate = fields.Float(u"Taux d'achèvement ", compute="_get_completion_rate", store=True)
    related_wbs_ids = fields.One2many('project.wbs.relation', 'wbs_id', u"Activités connexes")

    # resources_wbs_ids = fields.One2many('project.wbs.resources', 'wbs_id', u"Resources")

    high_plan_id = fields.Many2one("project.wbs", string="Parent de haut niveau")

    milestone_ids = fields.One2many("project.wbs", string="Jalons", compute="get_milestones")

    wbs_uid = fields.Char(u"UID")
    task_count = fields.Integer(compute="get_task_count", string=u"# Tâches", store=True)

    end_date_state = fields.Selection([
                                     ('green', 'Green'),
                                     ('orange', 'Orange'),
                                     ('red', 'Red'),
                                     ], compute='get_end_date_state', string='État de la date de fin', store=True)

    long_name = fields.Char(string="Description longue", compute="get_long_name", store=True)

    budget_ids = fields.One2many('account.analytic.line', 'wbs_id', 'Lignes du budget',
                                 domain=[('type', '=', 'f')])
    cost_ids = fields.One2many('account.analytic.line', 'wbs_id', 'Lignes du coût',
                               domain=[('type', '=', 'a')])

    qty = fields.Float(u'Quantité')
    unit_price = fields.Float(u'Prix unitaire (HT)')
    uom_id = fields.Many2one('uom.uom', string=u'UdM')
    total_price = fields.Float(u'Prix total', compute='get_price', store=True)
    product_id = fields.Many2one('product.product',u'Produit de facturation')

    @api.constrains('uom_id', 'product_id')
    def check_uom_id(self):
        for rec in self:
            if rec.uom_id and rec.product_id and rec.uom_id.category_id != rec.product_id.uom_id.category_id:
                raise ValidationError("L'unité de mesure de la ligne %s n'appartient pa à la catégorie"
                                      " de l'unité de mesure de l'article de facturation"%(rec.name))

    @api.onchange('product_id')
    def onchange_product(self):
        self.uom_id = self.product_id.uom_id.id

    @api.model
    def create_wbs_gantt(self, wbs_data):
        print("create_wbs_gantt", wbs_data)
        wbs_id = self.create(wbs_data)
        task_data = {'name': wbs_data['name'],
                     'date_start': wbs_data['start_date'],
                     'date_deadline': wbs_data['finish_date'],
                     'project_id': wbs_data['project_id'],
                     'wbs_id': wbs_id.id
                     }
        self.env['project.task'].create(task_data)
        return wbs_id.id

    @api.model
    def update_wbs_gantt(self, wbs_id, wbs_data, progress):
        wbs = self.browse(wbs_id)
        wbs.write(wbs_data)
        if not wbs.has_childs:
            for task in wbs.task_ids:
                task.reported_completion_rate = round(progress * 100, 0)
        return wbs


    def get_has_childs(self):
        for record in self:
            record.has_childs = len(record.child_ids) and True

    @api.onchange('qty','unit_price')
    def onchange_qty_unit_price(self):
        if (self.qty > 0 or self.unit_price > 0) and (not self.has_childs):
            self.is_invoicable = True
        else:
            self.is_invoicable = False


    @api.depends('qty', 'unit_price')
    def get_price(self):
        for record in self:
            record.total_price = record.unit_price * record.qty

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        if self.parent_id:
            self.parent_id.qty = 0
            self.parent_id.unit_price = 0
            self.parent_id.is_invoicable = False


    def action_open_budget(self):
        self.ensure_one()
        tree_view = self.env.ref('analytic.view_account_analytic_line_tree')
        form_view = self.env.ref('analytic.view_account_analytic_line_form')
        pivot_view = self.env.ref('analytic.view_account_analytic_line_pivot')
        budget_ids = [budget.id for budget in self.budget_ids]
        action = {
            'name': 'Prévu',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_type': 'form',
            'view_mode': 'tree,form,graph,pivot',
            'views': [(tree_view.id, 'tree'),(form_view.id,'form'),(pivot_view.id,'pivot')],
            'domain': [("id", "in", budget_ids), ('type', '=', 'f')],
            'context': {'type': 'f', 'default_type': 'f', 'default_project_id': self.project_id.id,
                        'default_wbs_id': self.id,
                        'default_account_id': self.project_id.analytic_account_id.id},
            'target': 'current',
        }
        return action


    def action_open_cost(self):
        tree_view = self.env.ref('analytic.view_account_analytic_line_tree')
        form_view = self.env.ref('analytic.view_account_analytic_line_form')
        pivot_view = self.env.ref('analytic.view_account_analytic_line_pivot')
        self.ensure_one()
        cost_ids = [cost.id for cost in self.cost_ids]
        action = {
            'name': 'Réel',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_type': 'form',
            'view_mode': 'tree,form,graph,pivot',
            'views': [(tree_view.id, 'tree'),(form_view.id,'form'),(pivot_view.id,'pivot')],
            'domain': [("id", "in", cost_ids), ('type', '=', 'a')],
            'context': {'type': 'a', 'default_type': 'a', 'default_project_id': self.project_id.id,
                        'default_wbs_id': self.id,
                        'default_account_id': self.project_id.analytic_account_id.id,
                        },
            'target': 'current',
        }
        return action


    @api.depends('name','code')
    def get_long_name(self):
        for record in self:
            record.long_name =str.join(':',(record.code,record.name))


    @api.depends('start_date', 'finish_date', 'is_milestone', 'completion_rate')
    def get_end_date_state(self):
        for rec in self:
            date_from = fields.Datetime.from_string(rec.start_date)
            date_to = fields.Datetime.from_string(rec.finish_date)
            current_date = fields.Datetime.from_string(fields.Datetime.now())
            if rec.is_milestone == False and rec.completion_rate != 100 and date_to and date_from:
                expected_duration = (date_to - date_from).days
                current_duration = (current_date - date_from).days
                duration_pourcentage = ((float(current_duration) - expected_duration) / (expected_duration or 1)) * 100
                if duration_pourcentage > 20.0:
                    rec.end_date_state = 'red'
                elif duration_pourcentage > 10.0:
                    rec.end_date_state = 'orange'
                elif duration_pourcentage > 0.0:
                    rec.end_date_state = 'green'


    @api.depends('task_ids')
    def get_task_count(self):
        for rec in self:
            rec.task_count = len(rec.task_ids)


    def name_get(self):
        return [(wbs.id, " - ".join([wbs.code, wbs.name])) for wbs in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        wbs = self.search(domain + args, limit=limit)
        return wbs.name_get()


    def get_milestones(self):
        for record in self:
            wbs_root = self.env['project.wbs'].search([('id', 'child_of', record.id),('is_milestone', '=', True)])
            if wbs_root:
                record.milestone_ids = wbs_root - record


    def get_high_level(self):
        for record in self:
            wbs_root = self.env['project.wbs'].search([('project_id', '=', record.project_id.id), ('parent_id', '=', False)])
            if wbs_root and record.is_milestone:
                parent_level_id = record
                level_id = False
                while wbs_root != parent_level_id:
                    level_id = parent_level_id
                    parent_level_id = parent_level_id.parent_id
                record.high_plan_id = level_id

    def daterange(self, date_from, date_to):
        date_to = fields.Date.from_string(date_to)
        date_from = fields.Date.from_string(date_from)
        for n in range(int((date_to - date_from).days) + 1):
            yield date_from + timedelta(n)

    def get_special_days(self, date_from, date_to):
        days_to_deduct = 0
        for date in self.daterange(date_from, date_to):
            if date.weekday() == 4:
                days_to_deduct += 1
            elif date.weekday() == 5:
                days_to_deduct += 1
        return days_to_deduct


    @api.depends('start_date', 'finish_date')
    def _get_duration(self):
        for record in self:
            if record.start_date and record.finish_date:
                start_date = record.start_date
                finish_date = record.finish_date

                record.duration = (finish_date-start_date).days
            else:
                record.duration = 0

    def _set_duration(self):
        for record in self:
            record.manuel_duration = record.duration


    def _get_cost(self):
        for record in self:
            if not record.child_ids:
                record.cost = sum([line.amount for line in record.cost_ids])
                record.budget = sum([line.amount for line in record.budget_ids])
            else:
                record.cost = sum([child.cost for child in record.child_ids])
                record.budget = sum([child.budget for child in record.child_ids])


    @api.depends('child_ids.completion_rate', 'child_ids.duration','task_ids.completion_rate',
                 'task_ids.planned_hours',
                 'duration', 'is_milestone_complete')
    def _get_completion_rate(self):
        for record in self:
            if record.is_milestone_complete:
                record.completion_rate = 100
            elif not record.child_ids:
                if record.task_ids:
                    record.completion_rate = sum([task.completion_rate * task.planned_hours for task in record.task_ids]) / \
                                             (sum([task.planned_hours for task in record.task_ids]) or 1.0)
                else:
                    record.completion_rate = 0
            else:
                list_childs = [child.completion_rate == 100 for child in record.child_ids.filtered(lambda r:r.duration != 0)]

                if len(list_childs) !=0 and all(list_childs):

                    record.completion_rate = 100

                else:
                    print('dddd',[child.weight for child in record.child_ids])

                    total_completion_rate = sum([child.completion_rate * child.weight for child in record.child_ids])

                    sum_weight = sum([child.weight for child in record.child_ids])
                    record.completion_rate = total_completion_rate / (sum_weight or 1.0)

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(u'Erreur ! Problème de parent récurrent')
        return True

    @api.constrains('code', 'code_client')
    def _check_code(self):
        list_code = self.code.split('.')
        for elem in list_code:
            try:
                int(elem)
            except:
                raise ValidationError(u'The code doit suivre le format: x.y.z (ex: 1.2.2.5)')
        return True


class Relation(models.Model):
    _name = 'project.wbs.relation'

    wbs_id = fields.Many2one('project.wbs', u"WBS")
    related_wbs_id = fields.Many2one('project.wbs', u"Activités connexes")
    relation = fields.Selection([('ff', 'Finish to finish'),
                                 ('fs','Finish to start'),
                                 ('ss', 'Start to start'),
                                 ('sf', 'Start to finish')], default='fs', string='Relation')
    lag = fields.Float(u"Lag (jours)")
