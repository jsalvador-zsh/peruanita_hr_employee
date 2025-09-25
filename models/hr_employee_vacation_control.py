from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class HrEmployeeVacationControl(models.Model):
    _name = 'hr.employee.vacation.control'
    _description = 'Control de Vacaciones por Empleado'
    _order = 'period_year desc, employee_id'
    _rec_name = 'display_name'

    @api.depends('employee_id', 'period_year')
    def _compute_display_name(self):
        for record in self:
            if record.employee_id and record.period_year:
                record.display_name = f"{record.employee_id.name} - {record.period_year}"
            else:
                record.display_name = "Nuevo Control de Vacaciones"

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
    
    period_year = fields.Integer(
        string='Año del Período',
        required=True,
        default=lambda self: date.today().year
    )
    
    period_start_date = fields.Date(
        string='Inicio del Período',
        required=True
    )
    
    period_end_date = fields.Date(
        string='Fin del Período',
        required=True
    )
    
    # Días de vacaciones
    days_earned_current_period = fields.Float(
        string='Días Ganados Período Actual',
        default=30.0,
        help='Días de vacaciones ganados en este período laboral'
    )
    
    days_from_previous_periods = fields.Float(
        string='Días de Períodos Anteriores',
        default=0.0,
        help='Días no tomados de períodos anteriores'
    )
    
    days_total_available = fields.Float(
        string='Total Días Disponibles',
        compute='_compute_days_totals',
        store=True,
        help='Total de días disponibles (período actual + anteriores)'
    )
    
    days_taken = fields.Float(
        string='Días Tomados',
        compute='_compute_days_taken',
        store=True,
        help='Total de días de vacaciones tomados'
    )
    
    days_pending = fields.Float(
        string='Días Pendientes',
        compute='_compute_days_totals',
        store=True,
        help='Días pendientes por tomar'
    )
    
    # Estado del período
    period_status = fields.Selection([
        ('active', 'Activo'),
        ('expired', 'Vencido'),
        ('closed', 'Cerrado')
    ], string='Estado del Período', default='active', required=True)
    
    # Control de fechas importantes
    deadline_to_take_vacations = fields.Date(
        string='Fecha Límite para Tomar Vacaciones',
        help='Fecha límite para tomar las vacaciones de este período'
    )
    
    is_vacation_granted = fields.Boolean(
        string='Vacaciones Otorgadas',
        default=False,
        help='Indica si ya se otorgaron formalmente las vacaciones al empleado'
    )
    
    vacation_granted_date = fields.Date(
        string='Fecha de Otorgamiento',
        help='Fecha en que se otorgaron las vacaciones'
    )
    
    # Observaciones y notas
    observations = fields.Text(
        string='Observaciones'
    )
    
    # Relación con las vacaciones tomadas
    vacation_taken_ids = fields.One2many(
        'hr.employee.vacation.taken',
        'vacation_control_id',
        string='Vacaciones Tomadas'
    )

    @api.depends('days_earned_current_period', 'days_from_previous_periods', 'days_taken')
    def _compute_days_totals(self):
        for record in self:
            record.days_total_available = record.days_earned_current_period + record.days_from_previous_periods
            record.days_pending = record.days_total_available - record.days_taken

    @api.depends('vacation_taken_ids.days_taken')
    def _compute_days_taken(self):
        for record in self:
            record.days_taken = sum(record.vacation_taken_ids.mapped('days_taken'))

    @api.constrains('period_start_date', 'period_end_date')
    def _check_period_dates(self):
        for record in self:
            if record.period_start_date and record.period_end_date:
                if record.period_start_date >= record.period_end_date:
                    raise ValidationError(_("La fecha de inicio del período debe ser anterior a la fecha de fin"))

    @api.constrains('employee_id', 'period_year')
    def _check_unique_period_per_employee(self):
        for record in self:
            existing = self.search([
                ('employee_id', '=', record.employee_id.id),
                ('period_year', '=', record.period_year),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError(_("Ya existe un control de vacaciones para este empleado en el año %s") % record.period_year)

    @api.onchange('period_year', 'period_start_date')
    def _onchange_period_year(self):
        if self.period_year and self.period_start_date:
            self.period_end_date = self.period_start_date + relativedelta(years=1, days=-1)
            self.deadline_to_take_vacations = self.period_end_date + relativedelta(months=12)

    @api.onchange('is_vacation_granted')
    def _onchange_vacation_granted(self):
        if self.is_vacation_granted and not self.vacation_granted_date:
            self.vacation_granted_date = fields.Date.context_today(self)
        elif not self.is_vacation_granted:
            self.vacation_granted_date = False

    def action_grant_vacation(self):
        """Acción para otorgar vacaciones"""
        self.ensure_one()
        self.is_vacation_granted = True
        self.vacation_granted_date = fields.Date.context_today(self)
        return True

    def action_close_period(self):
        """Acción para cerrar el período vacacional"""
        self.ensure_one()
        if self.days_pending > 0:
            # Crear siguiente período con los días pendientes
            next_period = self.env['hr.employee.vacation.control'].create({
                'employee_id': self.employee_id.id,
                'period_year': self.period_year + 1,
                'period_start_date': self.period_end_date + relativedelta(days=1),
                'period_end_date': self.period_end_date + relativedelta(years=1),
                'days_from_previous_periods': self.days_pending,
                'days_earned_current_period': 30.0,  # Días estándar
            })
        self.period_status = 'closed'
        return True

    @api.model
    def create_annual_vacation_periods(self, year=None):
        """Crear períodos vacacionales anuales para todos los empleados activos"""
        if not year:
            year = date.today().year
        
        employees = self.env['hr.employee'].search([('active', '=', True)])
        created_records = self.env['hr.employee.vacation.control']
        
        for employee in employees:
            existing = self.search([
                ('employee_id', '=', employee.id),
                ('period_year', '=', year)
            ])
            if not existing:
                # Calcular fecha de inicio basada en fecha de contratación o inicio de año
                start_date = date(year, 1, 1)
                if employee.contract_ids:
                    contract = employee.contract_ids.sorted('date_start', reverse=True)[0]
                    if contract.date_start.year == year:
                        start_date = contract.date_start
                
                record = self.create({
                    'employee_id': employee.id,
                    'period_year': year,
                    'period_start_date': start_date,
                    'period_end_date': date(year, 12, 31),
                    'days_earned_current_period': 30.0,
                })
                created_records += record
        
        return created_records


class HrEmployeeVacationTaken(models.Model):
    _name = 'hr.employee.vacation.taken'
    _description = 'Vacaciones Tomadas'
    _order = 'date_from desc'
    _rec_name = 'display_name'

    @api.depends('employee_id', 'date_from', 'date_to', 'days_taken')
    def _compute_display_name(self):
        for record in self:
            if record.employee_id and record.date_from:
                record.display_name = f"{record.employee_id.name} - {record.date_from} ({record.days_taken} días)"
            else:
                record.display_name = "Nueva Vacación Tomada"

    display_name = fields.Char(compute='_compute_display_name', store=True)
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Empleado',
        required=True,
        ondelete='cascade'
    )
    
    vacation_control_id = fields.Many2one(
        'hr.employee.vacation.control',
        string='Control de Vacaciones',
        required=True,
        ondelete='cascade'
    )
    
    date_from = fields.Date(
        string='Fecha de Inicio',
        required=True
    )
    
    date_to = fields.Date(
        string='Fecha de Fin',
        required=True
    )
    
    days_taken = fields.Float(
        string='Días Tomados',
        compute='_compute_days_taken',
        store=True,
        help='Días de vacaciones tomados (excluyendo fines de semana)'
    )
    
    include_weekends = fields.Boolean(
        string='Incluir Fines de Semana',
        default=False,
        help='Si está marcado, contará sábados y domingos como días de vacaciones'
    )
    
    vacation_type = fields.Selection([
        ('full', 'Vacaciones Completas'),
        ('partial', 'Vacaciones Parciales'),
        ('accumulated', 'Vacaciones Acumuladas')
    ], string='Tipo de Vacaciones', default='full', required=True)
    
    status = fields.Selection([
        ('planned', 'Planificadas'),
        ('approved', 'Aprobadas'),
        ('taken', 'Tomadas'),
        ('cancelled', 'Canceladas')
    ], string='Estado', default='planned', required=True)
    
    approved_by = fields.Many2one(
        'hr.employee',
        string='Aprobado por'
    )
    
    approval_date = fields.Date(
        string='Fecha de Aprobación'
    )
    
    observations = fields.Text(
        string='Observaciones'
    )

    @api.depends('date_from', 'date_to', 'include_weekends')
    def _compute_days_taken(self):
        for record in self:
            if record.date_from and record.date_to:
                if record.include_weekends:
                    delta = record.date_to - record.date_from
                    record.days_taken = delta.days + 1
                else:
                    # Contar solo días laborales (lunes a viernes)
                    current_date = record.date_from
                    days_count = 0
                    while current_date <= record.date_to:
                        if current_date.weekday() < 5:  # 0=Monday, 4=Friday
                            days_count += 1
                        current_date += relativedelta(days=1)
                    record.days_taken = days_count
            else:
                record.days_taken = 0

    @api.constrains('date_from', 'date_to')
    def _check_vacation_dates(self):
        for record in self:
            if record.date_from and record.date_to:
                if record.date_from > record.date_to:
                    raise ValidationError(_("La fecha de inicio de las vacaciones debe ser anterior a la fecha de fin"))

    @api.constrains('vacation_control_id', 'days_taken')
    def _check_available_days(self):
        for record in self:
            if record.vacation_control_id and record.days_taken:
                control = record.vacation_control_id
                other_taken = sum(control.vacation_taken_ids.filtered(lambda x: x.id != record.id).mapped('days_taken'))
                if (other_taken + record.days_taken) > control.days_total_available:
                    raise ValidationError(_("No hay suficientes días de vacaciones disponibles. Disponibles: %s, Intentando tomar: %s") % (control.days_total_available - other_taken, record.days_taken))

    def action_approve(self):
        """Aprobar las vacaciones"""
        self.ensure_one()
        self.status = 'approved'
        self.approved_by = self.env.user.employee_id.id
        self.approval_date = fields.Date.context_today(self)
        return True

    def action_mark_taken(self):
        """Marcar las vacaciones como tomadas"""
        self.ensure_one()
        self.status = 'taken'
        return True

    def action_cancel(self):
        """Cancelar las vacaciones"""
        self.ensure_one()
        self.status = 'cancelled'
        return True