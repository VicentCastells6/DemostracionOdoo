# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json
from odoo.exceptions import AccessError  # Importa AccessError si es necesario

class Prueba(http.Controller):

    @http.route('/equipo/prestamo/list', type='http', auth='public', methods=['GET'], csrf=False)
    def list_prestamos(self, **kw):
        """
        Muestra todos los préstamos como JSON desde el navegador.
        """
        try:
            prestamos = request.env['equipo.prestamo'].sudo().search([])
            prestamos_list = []
            for prestamo in prestamos:
                prestamos_list.append({
                    "id": prestamo.id,
                    "name": prestamo.name,
                    "employee": prestamo.employee_id.name if prestamo.employee_id else '',
                    "equipment": prestamo.equipment_id.name if prestamo.equipment_id else '',
                    "loan_date": str(prestamo.loanDate),
                    "return_date": str(prestamo.returnDate) if prestamo.returnDate else '',
                    "state": prestamo.state,
                    "description": prestamo.description,
                })

            json_data = json.dumps({"success": True, "prestamos": prestamos_list}, indent=4)
            return Response(json_data, content_type='application/json; charset=utf-8')
        
        except Exception as e:
            error_data = json.dumps({"success": False, "error": str(e)}, indent=4)
            return Response(error_data, content_type='application/json; charset=utf-8')
    
    @http.route('/prestamos/vista', type='http', auth='user', website=True)
    def prestamos_html_view(self, **kwargs):
        user = request.env.user

        # if not user.has_group('base.group_system'):  # Solo admins
        #     # Lanza la notificación sticky al partner conectado
        #     request.env['bus.bus']._sendone(
        #         user.partner_id.id,
        #         'simple_notification',
        #         {
        #             'title': "Acceso denegado",
        #             'message': "No tienes permiso para ver esta página 🔒",
        #             'sticky': True,
        #         }
        #     )
        #     # Redirige directamente a Discuss
        # return request.redirect('/web#menu_id=mail.mailbox_menu_discuss')

        # Si tiene permiso, muestra la vista
        prestamos = request.env['equipo.prestamo'].sudo().search([])
        return request.render('demostracionodoo.vista_prestamos_template', {
            'prestamos': prestamos
        })