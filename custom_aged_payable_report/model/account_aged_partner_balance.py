# -*- coding: utf-8 -*-
from odoo import models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import float_is_zero

class custom_report_account_aged_payable(models.AbstractModel):
    _inherit = "account.aged.payable"
    
    def _build_options(self, previous_options=None):
        options = super(custom_report_account_aged_payable, self)._build_options(previous_options=previous_options)
        if not previous_options:
            previous_options = {}
        options['currencies'] = self.get_currencies(previous_options)
        options['categories'] = self.get_categories(previous_options)
        return options
              
    def get_currencies(self,previous_options):
        # Get the currently selected option
        selected = None
        for opt in previous_options.get('currencies', []):
            if opt.get('selected'):
                selected = opt.get('id')
                
        records = self.env.user.company_id.currency_id + self.env['res.currency'].search([('active', '=', True), ('id', '!=', self.env.user.company_id.currency_id.id)], order="name")
        res = []
        for c in records:
            res.append({'id': c.id, 'name': c.name, 'selected': True if c.id == selected else False})
        return res
              
    def get_categories(self,previous_options):
        # Get the currently selected optionS
        categories = previous_options.get('categories', [])
        selected = [opt['id'] for opt in categories if opt.get('selected')]
        
        records = self.env['res.partner.category'].search([('active', '=', True)], order="name")
        res = []
        for c in records:
            res.append({'id': c.id, 'name': c.name, 'selected': True if c.id in selected else False })
        return res
    
    def set_context(self, options):
        ctx = super(custom_report_account_aged_payable, self).set_context(options)
        
        # Solo se puiede seleccionar una moneda o todas las monedas
        if options.get('currencies'):
            for j in options.get('currencies'):
                if j.get('selected'):
                    ctx['currency_id'] = j.get('id')
                    
        # Se pueden seleccionar varias categorias
        if options.get('categories'):
            ctx['category_ids'] = [j.get('id') for j in options.get('categories') if j.get('selected')]  
        return ctx

    def get_columns_name(self, options):
        ''' Cambiar etiquetas a dos columnas '''
        columns = [{}]
        columns += [{'name': v, 'class': 'number', 'style': 'white-space:nowrap;'} for v in [
            ("Al&nbsp;corriente&nbsp;").replace('&nbsp;', ' ') , 
            _("1&nbsp;-&nbsp;30").replace('&nbsp;', ' '),
            _("31&nbsp;-&nbsp;60").replace('&nbsp;', ' '),
            _("61&nbsp;-&nbsp;90").replace('&nbsp;', ' '),
            _("91&nbsp;-&nbsp;120").replace('&nbsp;', ' '),
            ("Mas&nbsp;de&nbsp;120&nbsp;dias").replace('&nbsp;', ' '), 
            _("Total")]]
        return columns
             
class CustomReportAgedPartnerBalance(models.AbstractModel):
    _inherit = 'report.account.report_agedpartnerbalance'

    def _get_partner_move_lines(self, account_type, date_from, target_move, period_length):            
        currency_id = self.env.context.get('currency_id', False)
        category_ids = self.env.context.get('category_ids', [])
        
        if currency_id or category_ids:
            return self._get_partner_move_lines_filtered(account_type, date_from, target_move, period_length, currency_id, category_ids)
        else:
            return super(CustomReportAgedPartnerBalance, self)._get_partner_move_lines(account_type, date_from, target_move, period_length)
                
    def _get_partner_move_lines_filtered(self, account_type, date_from, target_move, period_length,currency_id, category_ids):
        cr = self.env.cr
        # Sacados ids de res.partner con las etiquetas seleccionadas
        if category_ids:
            query = '''
                SELECT p.id FROM res_partner AS p
                INNER JOIN res_partner_res_partner_category_rel AS rel 
                ON p.id = rel.partner_id WHERE rel.category_id IN %s'''
            cr.execute(query, (tuple(category_ids),))

            recs = cr.dictfetchall()
            filtered_partner_ids = [partner['id'] for partner in recs if partner['id']]
            if not filtered_partner_ids:
                return [], [], {}
        else:
            filtered_partner_ids = False
        
        # This method can receive the context key 'include_nullified_amount' {Boolean}
        # Do an invoice and a payment and unreconcile. The amount will be nullified
        # By default, the partner wouldn't appear in this report.
        # The context key allow it to appear
        # In case of a period_length of 30 days as of 2019-02-08, we want the following periods:
        # Name       Stop         Start
        # 1 - 30   : 2019-02-07 - 2019-01-09
        # 31 - 60  : 2019-01-08 - 2018-12-10
        # 61 - 90  : 2018-12-09 - 2018-11-10
        # 91 - 120 : 2018-11-09 - 2018-10-11
        # +120     : 2018-10-10
        periods = {}
        start = datetime.strptime(date_from, "%Y-%m-%d")
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length)
            period_name = str((5-(i+1)) * period_length + 1) + '-' + str((5-i) * period_length)
            period_stop = (start - relativedelta(days=1)).strftime('%Y-%m-%d')
            if i == 0:
                period_name = '+' + str(4 * period_length)
            periods[str(i)] = {
                'name': period_name,
                'stop': period_stop,
                'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop

        res = []
        total = []
        # cr = self.env.cr
        ResCurrency = self.env['res.currency'].with_context(date=date_from)
        user_company = self.env.user.company_id
        
        # Creamos query para currency
        if currency_id:
            currency_clause = ' AND (l.currency_id = %s ' % currency_id 
            # account.move.line.currency_id puede estar vacio cuando
            # el movimiento esta en la misma moneda de la compania 
            if currency_id == self.env.user.currency_id.id:
                currency_clause += ' OR l.currency_id is Null) ' 
            else:
                currency_clause += ' ) '       
            user_currency = ResCurrency.browse(currency_id)       
        else:
            currency_clause = ''   
            user_currency = user_company.currency_id 
            
        # ResCurrency = self.env['res.currency'].with_context(date=date_from)
        company_ids = self._context.get('company_ids') or [user_company.id]
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']
        arg_list = (tuple(move_state), tuple(account_type))
        #build the reconciliation clause to see what partner needs to be printed
        reconciliation_clause = '(l.reconciled IS FALSE)'
        cr.execute('SELECT debit_move_id, credit_move_id FROM account_partial_reconcile where max_date > %s', (date_from,))
        reconciled_after_date = []
        for row in cr.fetchall():
            reconciled_after_date += [row[0], row[1]]
        if reconciled_after_date:
            reconciliation_clause = '(l.reconciled IS FALSE OR l.id IN %s)'
            arg_list += (tuple(reconciled_after_date),)
        arg_list += (date_from, tuple(company_ids))
        query = '''
            SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
            FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
            WHERE (l.account_id = account_account.id)
                AND (l.move_id = am.id)
                AND (am.state IN %s)
                AND (account_account.internal_type IN %s)
                AND ''' + reconciliation_clause + currency_clause + '''
                AND (l.date <= %s)
                AND l.company_id IN %s
            ORDER BY UPPER(res_partner.name)'''
        cr.execute(query, arg_list)

        partners = cr.dictfetchall()
        # put a total of 0
        for i in range(7):
            total.append(0)

        # Build a string like (1,2,3) for easy use in SQL query
        if filtered_partner_ids:
            partner_ids = [partner['partner_id'] for partner in partners if partner['partner_id'] and partner['partner_id'] in filtered_partner_ids]
        else:
            partner_ids = [partner['partner_id'] for partner in partners if partner['partner_id']]
        lines = dict((partner['partner_id'] or False, []) for partner in partners)
        if not partner_ids:
            return [], [], {}

        # This dictionary will store the not due amount of all partners
        undue_amounts = {}
        query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND (COALESCE(l.date_maturity,l.date) >= %s)\
                    AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                AND (l.date <= %s) ''' + currency_clause + '''
                AND l.company_id IN %s''' 
        cr.execute(query, (tuple(move_state), tuple(account_type), date_from, tuple(partner_ids), date_from, tuple(company_ids)))
        aml_ids = cr.fetchall()
        aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        for line in self.env['account.move.line'].browse(aml_ids):
            partner_id = line.partner_id.id or False
            if partner_id not in undue_amounts:
                undue_amounts[partner_id] = 0.0
            # Si el movimiento ya esta en la moneda solicitada que no convierta
            if currency_id and currency_id == line.currency_id.id:
                line_amount = line.amount_currency
            else:
                line_amount = ResCurrency._compute(line.company_id.currency_id, user_currency, line.balance)
            if user_currency.is_zero(line_amount):
                continue
            for partial_line in line.matched_debit_ids:
                if partial_line.max_date <= date_from:
                    # Si el movimiento ya esta en la moneda solicitada que no convierta
                    if currency_id and currency_id == partial_line.currency_id.id:
                        line_amount += partial_line.amount_currency
                    else:
                        line_amount += ResCurrency._compute(partial_line.company_id.currency_id, user_currency, partial_line.amount)
            for partial_line in line.matched_credit_ids:
                if partial_line.max_date <= date_from:
                    # Si el movimiento ya esta en la moneda solicitada que no convierta
                    if currency_id and currency_id == partial_line.currency_id.id:
                        line_amount -= partial_line.amount_currency
                    else:
                        line_amount -= ResCurrency._compute(partial_line.company_id.currency_id, user_currency, partial_line.amount)
            if not self.env.user.company_id.currency_id.is_zero(line_amount):
                undue_amounts[partner_id] += line_amount
                lines[partner_id].append({
                    'line': line,
                    'amount': line_amount,
                    'period': 6,
                })

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(account_type), tuple(partner_ids),)
            dates_query = '(COALESCE(l.date_maturity,l.date)'

            if periods[str(i)]['start'] and periods[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (periods[str(i)]['start'], periods[str(i)]['stop'])
            elif periods[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (periods[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (periods[str(i)]['stop'],)
            args_list += (date_from, tuple(company_ids))

            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                        AND ''' + dates_query + currency_clause + '''
                    AND (l.date <= %s)
                    AND l.company_id IN %s'''
            cr.execute(query, args_list)
            partners_amount = {}
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids).with_context(prefetch_fields=False):
                partner_id = line.partner_id.id or False
                if partner_id not in partners_amount:
                    partners_amount[partner_id] = 0.0
                # Si el movimiento ya esta en la moneda solicitada que no convierta
                if currency_id and currency_id == line.currency_id.id:
                    line_amount = line.amount_currency
                else:
                    line_amount = ResCurrency._compute(line.company_id.currency_id, user_currency, line.balance)
                if user_currency.is_zero(line_amount):
                    continue
                for partial_line in line.matched_debit_ids:
                    if partial_line.max_date <= date_from:
                        # Si el movimiento ya esta en la moneda solicitada que no convierta
                        if currency_id and currency_id == partial_line.currency_id.id:
                            line_amount += partial_line.amount_currency
                        else:
                            line_amount += ResCurrency._compute(partial_line.company_id.currency_id, user_currency, partial_line.amount)
                for partial_line in line.matched_credit_ids:
                    if partial_line.max_date <= date_from:
                        # Si el movimiento ya esta en la moneda solicitada que no convierta
                        if currency_id and currency_id == partial_line.currency_id.id:
                            line_amount -= partial_line.amount_currency
                        else:
                            line_amount -= ResCurrency._compute(partial_line.company_id.currency_id, user_currency, partial_line.amount)

                if not self.env.user.company_id.currency_id.is_zero(line_amount):
                    partners_amount[partner_id] += line_amount
                    lines[partner_id].append({
                        'line': line,
                        'amount': line_amount,
                        'period': i + 1,
                        })
            history.append(partners_amount)

        for partner in partners:
            if partner['partner_id'] is None:
                partner['partner_id'] = False
            at_least_one_amount = False
            values = {}
            undue_amt = 0.0
            if partner['partner_id'] in undue_amounts:  # Making sure this partner actually was found by the query
                undue_amt = undue_amounts[partner['partner_id']]

            total[6] = total[6] + undue_amt
            values['direction'] = undue_amt
            if not float_is_zero(values['direction'], precision_rounding=self.env.user.company_id.currency_id.rounding):
                at_least_one_amount = True

            for i in range(5):
                during = False
                if partner['partner_id'] in history[i]:
                    during = [history[i][partner['partner_id']]]
                # Adding counter
                total[(i)] = total[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
                if not float_is_zero(values[str(i)], precision_rounding=self.env.user.company_id.currency_id.rounding):
                    at_least_one_amount = True
            values['total'] = sum([values['direction']] + [values[str(i)] for i in range(5)])
            ## Add for total
            total[(i + 1)] += values['total']
            values['partner_id'] = partner['partner_id']
            if partner['partner_id']:
                browsed_partner = self.env['res.partner'].browse(partner['partner_id'])
                values['name'] = browsed_partner.name and len(browsed_partner.name) >= 45 and browsed_partner.name[0:40] + '...' or browsed_partner.name
                values['trust'] = browsed_partner.trust
            else:
                values['name'] = _('Unknown Partner')
                values['trust'] = False

            if at_least_one_amount or (self._context.get('include_nullified_amount') and lines[partner['partner_id']]):
                res.append(values)
 
        return res, total, lines
