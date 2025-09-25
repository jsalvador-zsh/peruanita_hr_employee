{
    'name': 'Peruanita HR Employee Extensions',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Gestión de salidas, distribuciones y permisos de empleados',
    'description': """
        Módulo para gestionar:
        - Salidas de empleados
        - Salidas por distribución
        - Salidas por permisos
        
        Incluye smart buttons en el empleado para ver todos sus registros relacionados.
    """,
    'author': 'Juan Salvador',
    'website': 'https://juansalvador.dev',
    'depends': ['hr', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_exit_views.xml',
        'views/hr_employee_distribution_views.xml',
        'views/hr_employee_permission_views.xml',
        'views/hr_employee_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}