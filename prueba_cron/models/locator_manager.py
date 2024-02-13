from odoo import models, fields

class LocatorManager(models.Model):
    _name = "locator.management"

    def cron_check_locators_debug_date(self):
            """ Planned action that is executed daily and sends an email message to the
            person responsible for the locators to notify them that they have to debug it"""

            locators_debug = self.search([]).filtered(lambda x: (x.deadline_assign_locators - fields.datetime.now()).days == 10)

            for rec in locators_debug:
                template_id = self.env.ref('b_locator_management.b_locator_management_email_template_debugged')
                template_id.sudo().send_mail(rec.id, force_send=True)