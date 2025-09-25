from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEmployeePermission(models.Model):
    _name = 'hr.employee.permission'
    _description = 'Salidas por Permiso'
    _order = 'date desc, id desc'
    _rec_name = 'display_name'

    @api.depends('employee_id', 'date', 'permission_reason')
    def _compute_display_name(self):
        for record in self:
            if record.employee_id and record.date:
                reason = dict(record._fields['permission_reason'].selection).get(record.permission_reason, '')
                record.display_name = f"{record.employee_id.name} - {record.date} - {reason}"
            else:
                record.display_name = "Nuevo Permiso"

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
    
    # Cantidad de días
    days_quantity = fields.Integer(
        string='Cantidad de Días',
        default=1
    )
    
    date_from = fields.Date(
        string='Desde el Día'
    )
    
    date_to = fields.Date(
        string='Hasta el Día'
    )
    
    # Horas
    hours_quantity = fields.Float(
        string='Cantidad de Horas'
    )
    
    time_from = fields.Float(
        string='Desde la Hora',
        help='Hora en formato 24h (ej: 14.5 = 14:30)'
    )
    
    time_to = fields.Float(
        string='Hasta la Hora',
        help='Hora en formato 24h (ej: 17.5 = 17:30)'
    )
    
    # Se compensa con
    compensation_type = fields.Selection([
        ('vacation', 'A cuenta de vacaciones'),
        ('unpaid_leave', 'Licencia sin goce'),
        ('compensate_hours', 'Compensa horas')
    ], string='Se Compensa Con', required=True)
    
    # Motivo de permiso
    permission_reason = fields.Selection([
        ('personal', 'Motivos personales'),
        ('illness_no_essalud', 'Enfermedad sin atención ESSALUD'),
        ('medical_appointment', 'Cita médica'),
        ('other', 'Otros')
    ], string='Motivo de Permiso', required=True)
    
    permission_reason_detail = fields.Text(
        string='Detalle del Motivo',
        help='Especificar cuando se selecciona "Otros"'
    )
    
    observations = fields.Text(
        string='Observaciones'
    )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to:
                if record.date_from > record.date_to:
                    raise ValidationError(_("La fecha 'Desde el Día' no puede ser posterior a 'Hasta el Día'"))

    @api.constrains('time_from', 'time_to')
    def _check_times(self):
        for record in self:
            if record.time_from and record.time_to:
                if record.time_from >= record.time_to:
                    raise ValidationError(_("La hora 'Desde' debe ser anterior a la hora 'Hasta'"))

    @api.constrains('permission_reason', 'permission_reason_detail')
    def _check_reason_detail(self):
        for record in self:
            if record.permission_reason == 'other' and not record.permission_reason_detail:
                raise ValidationError(_("Debe especificar el detalle cuando selecciona 'Otros' como motivo"))

    @api.onchange('date_from', 'date_to')
    def _onchange_dates(self):
        if self.date_from and self.date_to:
            delta = self.date_to - self.date_from
            self.days_quantity = delta.days + 1

    @api.onchange('time_from', 'time_to')
    def _onchange_times(self):
        if self.time_from and self.time_to:
            self.hours_quantity = self.time_to - self.time_from

    def name_get(self):
        result = []
        for record in self:
            reason = dict(record._fields['permission_reason'].selection).get(record.permission_reason, '')
            name = f"{record.employee_id.name} - {record.date} - {reason}"
            if record.days_quantity > 1:
                name += f" ({record.days_quantity} días)"
            elif record.hours_quantity:
                name += f" ({record.hours_quantity}h)"
            result.append((record.id, name))
        return result