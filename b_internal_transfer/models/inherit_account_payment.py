
from odoo import api, models, fields, _


class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    
    #Campos de diario contrapartida
    destination_journal_id = fields.Many2one('account.journal', string='Counterpart Journal', readonly=True, states={'draft': [('readonly', False)]}, tracking=True, domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]", default="")
    counterpart_amount = fields.Monetary(currency_field='counterpart_currency_id', readonly=True)
    counterpart_currency_id = fields.Many2one('res.currency', string='Counterpart Currency', store=True, readonly=True,
        states={'draft': [('readonly', False)]}, default=lambda self: self.env.company.currency_id)
    counterpart_inbound = fields.Boolean(default=False)
    
    #Campo para tipo de cambio personalizado
    enable_customized_type_exchange = fields.Boolean(default = False, string="Enable customized exchange")
    customized_type_exchange = fields.Float(
        string='Customized type exchange',
        digits=(12, 6)
    )
    #Campo para mostrar tipo de cambion personzalizado
    show_customized_type_exchange = fields.Boolean(default=False)
    
    #Campo para mostrar  campos en vista de modelo account.payment
    show_type_exchange = fields.Boolean(default=False)
    
    #Campo para tipo de cambio
    type_exchange = fields.Float(
        string='Type exchange',
        digits=(12, 6),
        readonly=True
    )
    #Campo para apuntes contables contrapartida
    paired_internal_transfer_payment_id = fields.Many2one('account.payment',
        help="When an internal transfer is posted, a paired payment is created. "
        "They are cross referenced trough this field")
    
    
 ############################################### DECORADORES ############################################ 
    

    #Decorador para conversión de monto o importe de banco 1 a importe de banco 2
    @api.onchange('amount','counterpart_amount','currency_id','counterpart_currency_id','date','customized_type_exchange')
    def _depends_counterpart_amount(self):
        rate = self.type_exchange
        convertion = self.currency_id.with_context(
                    use_custom_rate=True,
                    custom_rate=rate)._convert(
                        self.amount,
                        self.counterpart_currency_id,
                        self.company_id, self.date
                    )
        self.counterpart_amount = convertion
        if self.enable_customized_type_exchange == True:
            convertion = self.customized_type_exchange
            self.counterpart_amount = convertion * self.amount
        
     #Decorador para mostrar tipo de cambio
    @api.onchange('date','currency_id')
    def _onchange_payment_date(self):
        for payment in self:
            if fields.Date.today() >= self.date:
                if  payment.currency_id.id != payment.company_id.currency_id.id:
                    currency_rates = payment.currency_id._get_rates(
                        payment.company_id, (payment.date or fields.Date.today()))
                    currency_rate = 1 / (currency_rates.get(
                        payment.currency_id.id) or payment.currency_id.rate)
                    payment.type_exchange = currency_rate
                    
                    
    #Decorador para mostrar tipo de cambio personalizado         
    @api.onchange('show_type_exchange','currency_id')
    def _onchange_currency(self):
        if self.currency_id != self.company_id.currency_id:
            self.show_type_exchange = True
        else:
            self.show_type_exchange = False
            
            
    #Decorador para mostrar tipo de cambio personalizado       
    @api.onchange('show_customized_type_exchange','currency_id')
    def _onchange_customized_currency(self):
        if self.currency_id != self.company_id.currency_id:
            self.show_customized_type_exchange = True
        else:
            self.show_customized_type_exchange = False
            
 ############################################### MÉTODOS ############################################ 
            
    #Acción de crear nuevo record al confirmar 
    def action_post(self):
        ''' draft -> posted '''
        self.move_id._post(soft=False)

        self.filtered(
            lambda pay: pay.is_internal_transfer and not pay.paired_internal_transfer_payment_id
        )._create_paired_internal_transfer_payment()
        
        
    #Diccionario para creación de pago 
    def _create_paired_internal_transfer_payment(self):
        ''' When an internal transfer is posted, a paired payment is created
        with opposite payment_type and swapped journal_id & destination_journal_id.
        Both payments liquidity transfer lines are then reconciled.
        '''
        for payment in self:
            paired_payment = payment.copy({
                'journal_id': payment.destination_journal_id.id,
                'destination_journal_id': payment.journal_id.id,
                'payment_type': payment.payment_type == 'outbound' and 'inbound' or 'outbound',
                'move_id': None,
                'ref': payment.name,
                'paired_internal_transfer_payment_id': payment.id,
                'date': payment.date,
            })
            #Actualización de diccionario para cambio de monto y moneda en diario a recibir transferencia
            paired_payment.update({
                'currency_id': self.counterpart_currency_id, 
                'amount': self.counterpart_amount,
            })
            paired_payment.move_id._post(soft=False)
            payment.paired_internal_transfer_payment_id = paired_payment

            body = _('This payment has been created from <a href=# data-oe-model=account.payment data-oe-id=%d>%s</a>') % (payment.id, payment.name)
            paired_payment.message_post(body=body)
            body = _('A second payment has been created: <a href=# data-oe-model=account.payment data-oe-id=%d>%s</a>') % (paired_payment.id, paired_payment.name)
            payment.message_post(body=body)

            lines = (payment.move_id.line_ids + paired_payment.move_id.line_ids).filtered(
                lambda l: l.account_id == payment.destination_account_id and not l.reconciled)
            lines.reconcile()
