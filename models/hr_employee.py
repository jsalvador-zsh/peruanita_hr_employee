from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Campos computados para contar registros
    exit_count = fields.Integer(
        string='Salidas',
        compute='_compute_records_count'
    )
    
    distribution_count = fields.Integer(
        string='Distribuciones',
        compute='_compute_records_count'
    )
    
    permission_count = fields.Integer(
        string='Permisos',
        compute='_compute_records_count'
    )

    vacation_control_count = fields.Integer(
        string='Control de Vacaciones',
        compute='_compute_records_count'
    )

    @api.depends('name')
    def _compute_records_count(self):
        for employee in self:
            employee.exit_count = self.env['hr.employee.exit'].search_count([
                ('employee_id', '=', employee.id)
            ])
            
            employee.distribution_count = self.env['hr.employee.distribution'].search_count([
                ('employee_id', '=', employee.id)
            ])
            
            employee.permission_count = self.env['hr.employee.permission'].search_count([
                ('employee_id', '=', employee.id)
            ])

            employee.vacation_control_count = self.env['hr.employee.vacation.control'].search_count([
                ('employee_id', '=', employee.id)
            ])

    def action_view_exits(self):
        """Acción para mostrar las salidas del empleado"""
        self.ensure_one()
        tree_view_id = self.env.ref('peruanita_hr_employee.view_hr_employee_exit_tree').id
        form_view_id = self.env.ref('peruanita_hr_employee.view_hr_employee_exit_form').id
        return {
            'name': f'Salidas de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.exit',
            'view_mode': 'list,form',
            'views': [(tree_view_id, 'list'), (form_view_id, 'form')],
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'default_employee_id': self.id,
                'create': True,
            },
            'target': 'current',
        }

    def action_view_distributions(self):
        """Acción para mostrar las distribuciones del empleado"""
        self.ensure_one()
        tree_view_id = self.env.ref('peruanita_hr_employee.view_hr_employee_distribution_tree').id
        form_view_id = self.env.ref('peruanita_hr_employee.view_hr_employee_distribution_form').id
        return {
            'name': f'Distribuciones de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.distribution',
            'view_mode': 'list,form',
            'views': [(tree_view_id, 'list'), (form_view_id, 'form')],
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'default_employee_id': self.id,
                'create': True,
            },
            'target': 'current',
        }

    def action_view_permissions(self):
        """Acción para mostrar los permisos del empleado"""
        self.ensure_one()
        tree_view_id = self.env.ref('peruanita_hr_employee.view_hr_employee_permission_tree').id
        form_view_id = self.env.ref('peruanita_hr_employee.view_hr_employee_permission_form').id
        return {
            'name': f'Permisos de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.permission',
            'view_mode': 'list,form',
            'views': [(tree_view_id, 'list'), (form_view_id, 'form')],
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'default_employee_id': self.id,
                'create': True,
            },
            'target': 'current',
        }
    
    def action_view_vacation_control(self):
        """Acción para mostrar el control de vacaciones del empleado"""
        self.ensure_one()
        tree_view_id = self.env.ref('peruanita_hr_employee.view_hr_employee_vacation_control_tree').id
        form_view_id = self.env.ref('peruanita_hr_employee.view_hr_employee_vacation_control_form').id
        return {
            'name': f'Control de Vacaciones - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.vacation.control',
            'view_mode': 'list,form',
            'views': [(tree_view_id, 'list'), (form_view_id, 'form')],
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'default_employee_id': self.id,
                'create': True,
            },
            'target': 'current',
        }