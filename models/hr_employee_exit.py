from odoo import api, fields, models


class HrEmployeeExit(models.Model):
    _name = 'hr.employee.exit'
    _description = 'Salidas de Empleados'
    _order = 'date desc, id desc'
    _rec_name = 'display_name'

    @api.depends('employee_id', 'date', 'exit_reason')
    def _compute_display_name(self):
        for record in self:
            if record.employee_id and record.date:
                record.display_name = f"{record.employee_id.name} - {record.date} - {record.exit_reason or 'Sin motivo'}"
            else:
                record.display_name = "Nueva Salida"

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
            name = f"{record.employee_id.name} - {record.date}"
            if record.exit_reason:
                name += f" - {record.exit_reason[:50]}..."
            result.append((record.id, name))
        return result