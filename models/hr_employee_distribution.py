from odoo import api, fields, models


class HrEmployeeDistribution(models.Model):
    _name = 'hr.employee.distribution'
    _description = 'Salidas por Distribución'
    _order = 'date desc, id desc'
    _rec_name = 'display_name'

    @api.depends('employee_id', 'date', 'distribution_type')
    def _compute_display_name(self):
        for record in self:
            if record.employee_id and record.date:
                dist_type = dict(record._fields['distribution_type'].selection).get(record.distribution_type, '')
                record.display_name = f"{record.employee_id.name} - {record.date} - {dist_type}"
            else:
                record.display_name = "Nueva Distribución"

    display_name = fields.Char(compute='_compute_display_name', store=True)
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Empleado',
        required=True,
        ondelete='cascade'
    )
    
    job_id = fields.Many2one(
        'hr.job',
        string='Puesto de Trabajo',
        related='employee_id.job_id',
        store=True
    )
    
    department_id = fields.Many2one(
        'hr.department',
        string='Departamento',
        related='employee_id.department_id',
        store=True
    )
    
    date = fields.Date(
        string='Fecha',
        required=True,
        default=fields.Date.context_today
    )
    
    exit_reason = fields.Text(
        string='Motivo de Salida',
        required=True
    )
    
    route = fields.Char(
        string='Ruta',
        required=True
    )
    
    distribution_type = fields.Selection([
        ('city', 'Ciudad'),
        ('travel', 'Viaje')
    ], string='Distribución', required=True, default='city')
    
    exit_time = fields.Float(
        string='Hora de Salida',
        help='Hora en formato 24h (ej: 14.5 = 14:30)'
    )
    
    arrival_time = fields.Float(
        string='Hora de Llegada',
        help='Hora en formato 24h (ej: 17.5 = 17:30)'
    )
    
    entry_time = fields.Float(
        string='Hora de Entrada',
        help='Hora en formato 24h (ej: 8.0 = 08:00)'
    )
    
    observations = fields.Text(
        string='Observaciones'
    )

    def name_get(self):
        result = []
        for record in self:
            dist_type = dict(record._fields['distribution_type'].selection).get(record.distribution_type, '')
            name = f"{record.employee_id.name} - {record.date} - {dist_type}"
            if record.route:
                name += f" ({record.route})"
            result.append((record.id, name))
        return result