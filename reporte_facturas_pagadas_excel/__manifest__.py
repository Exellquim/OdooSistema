{
    "name": "Reporte Facturas Pagadas Excel",
    "summary": "Exporta relación entre facturas y pagos a Excel",
    "version": "17.0.1.0.0",
    "category": "Accounting",
    "author": "RBS-HELP2025",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/facturas_pagadas_excel_wizard_view.xml",
    ],
    "installable": True,
    "application": False,
}
