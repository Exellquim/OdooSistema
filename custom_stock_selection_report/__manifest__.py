{
    'name': 'Stock Picking Product Selection Report',
    'version': '1.0',
    'depends': ['stock', 'purchase'],
    'category': 'Inventory',
    'summary': 'Permite seleccionar productos del picking y generar un reporte',
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/picking_product_select_wizard_views.xml',
        
    ],
    'installable': True,
    'application': False,
}
