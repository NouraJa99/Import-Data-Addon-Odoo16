# -*- coding: utf-8 -*-
import binascii
import datetime
from datetime import datetime
import xlrd
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
import tempfile
#import csv
import xmlrpc.client
import pandas as pd

import binascii
import datetime
from datetime import datetime
import xlrd
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
import tempfile
#import csv
import xmlrpc.client

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    upload_operations = fields.Many2many('ir.attachment',string= "Upload Operations")
    def import_xls(self):
        for data_file in self.upload_operations:
            file_name = data_file.name.lower()
            if file_name.strip().endswith('.xlsx'):
                try:
                    fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                    fp.write(binascii.a2b_base64(data_file.datas))
                    fp.seek(0)
                    values = {}
                    workbook = xlrd.open_workbook(fp.name)
                    sheet = workbook.sheet_by_index(0)

                except:
                    raise UserError(_("Invalid file!"))
                vals_list = []
                for row_no in range(sheet.nrows):
                    val = {}
                    values = {}
                    if row_no <= 0:
                        fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                    else:
                        line = list(map(
                            lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(
                                row.value), sheet.row(row_no)))

                        seconds = (float(line[8]) - 25569) * 86400.0
                        l2date = datetime.utcfromtimestamp(seconds)

                        product = self.env['product.product'].search([('name', '=', str(line[0]))])
                        if product:
                            values.update({'product_id': product.id, })

                        source = self.env['stock.location'].search([('name', '=', str(line[1]))])
                        print("Here is the source: ", source)
                        if source:
                            values.update({'location_id': source.id, })

                        owner = self.env['res.partner'].search([('name', '=', str(line[2]))])
                        if owner:
                            values.update({'owner_id': owner.id,})

                        serial= self.env['stock.lot'].search([('name', '=', str(line[3]))])
                        if serial:
                            values.update({'lot_id': serial.id,})

                        values.update({'lot_name':line[3]})

                        values.update({'qty_done':float(line[4])})
                        values.update({'date': l2date})

                        company = self.env['res.company'].search([('name', '=', str(line[5]))])
                        print("Here is the company: ", company)
                        if company:
                             values.update({'company_id': company.id,})

                        uom = self.env['uom.uom'].search([('name', '=', str(line[7]))])
                        print("Here is the uom ", uom)
                        if uom:
                              values.update({'product_uom_id': uom.id, })

                        dest = self.env['stock.location'].search([('name', '=', str(line[6]))])
                        print("Here is the dest): ", dest)

                        if dest:
                              values.update({'location_dest_id': dest.id,})
                              print("Here is the id: ", dest.id)


                        vals_list.append(values)
                        #vals_list.append(values.copy())
                        print(vals_list)


                if len(vals_list) != 0:
                    url = 'http://localhost:8016'
                    db = 'Test_ERP'
                    username = 'admin'
                    password = 'admin'
                    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
                    uid = common.authenticate(db, username, password, {})

                    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
                    #created_id = models.execute_kw(db, uid, password, 'stock.move.line', 'create', [vals_list])
                    #self.write({'move_ids_without_package': created_id})
                    print("Here is the list:", vals_list)
                    return(vals_list)

            else:
                raise UserError(_("Invalid file type!"))



    def import_receipt_data(self):
        vals_list = self.import_xls()
        print("Here is the second list", vals_list )
        for val in vals_list:
            print("This is the val:", val)
            self.env['stock.move.line'].create({'picking_id': self.id,
                                                'product_id': val.get('product_id'),
                                                'company_id': val.get('company_id'),
                                                'product_uom_id': val.get('product_uom_id'),
                                                'lot_id': val.get('lot_id'),
                                                'qty_done': 1,
                                                'location_id': val.get('location_id'),
                                                'location_dest_id': val.get('location_dest_id'),
                                                'lot_name': val.get('lot_name'),
                                                'owner_id': val.get('owner_id'),
                                                })


#This second part is dedicated for importing data directly from
#RMA reporting and then create a new table easily exploited to fill out lines in odoo
#Detailed operations tab



    def import_rma_inventory(self):
        calculated_data = []
        for data_file in self.upload_operations:
            file_name = data_file.name.lower()
            print(file_name)
            #if file_name.strip().endswith('.xlsx'):
            if file_name.strip().endswith('.csv'):
                try:
                    #fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                    fp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
                    fp.write(binascii.a2b_base64(data_file.datas))
                    fp.seek(0)
                    #df = pd.read_excel(fp.name, header=0, skiprows=0, usecols=range(24, 28))
                    df = pd.read_csv(fp.name)
                    seconds = (float(2-2-2023) - 25569) * 86400.0
                    l2date = datetime.utcfromtimestamp(seconds)
                    col_24_sum = df.iloc[:, 24].sum()
                    if col_24_sum != 0:
                        print("Test value here", col_24_sum)
                        calculated_data.append({
                            "product_id": "Sandisk ultra 32GB SD card",
                            "qty_done": col_24_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })

                    col_25_sum = df.iloc[:, 25].sum()
                    if col_25_sum != 0:
                        calculated_data.append({
                            "product_id": "Orange pi Zero",
                            "qty_done": col_25_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })

                    col_26_sum = df.iloc[:, 26].sum()
                    if col_26_sum != 0:
                        calculated_data.append({
                            "product_id": "I/O PCB",
                            "qty_done": col_26_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })

                    col_27_sum = df.iloc[:, 27].sum()
                    if col_27_sum != 0:
                        calculated_data.append({
                            "product_id": "Temperature sensor",
                            "qty_done": col_27_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })

                    col_28_sum = df.iloc[:, 28].sum()
                    if col_28_sum != 0:
                        calculated_data.append({
                            "product_id": "Front dial piece",
                            "qty_done": col_28_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })
                    col_30_sum = df.iloc[:, 30].sum()
                    if col_30_sum != 0:
                        calculated_data.append({
                            "product_id": "Stepper Motor",
                            "qty_done": col_30_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })
                    col_31_sum = df.iloc[:, 31].sum()
                    if col_28_sum != 0:
                        calculated_data.append({
                            "product_id": "Sensor PCB",
                            "qty_done": col_31_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })
                    col_34_sum = df.iloc[:, 34].sum()
                    if col_34_sum != 0:
                        calculated_data.append({
                            "product_id": "Ethernet cable",
                            "qty_done": col_34_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })
                    col_37_sum = df.iloc[:, 37].sum()
                    if col_37_sum != 0:
                        calculated_data.append({
                            "product_id": "Ethernet PCB",
                            "qty_done": col_37_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })
                    col_38_sum = df.iloc[:, 38].sum()
                    if col_38_sum != 0:
                        calculated_data.append({
                            "product_id": "Power brick",
                            "qty_done": col_38_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })

                    col_39_sum = (df.iloc[:, 39].sum())*4

                    if col_39_sum != 0:
                        calculated_data.append({
                            "product_id": "Sensor battery",
                            "qty_done": col_39_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })
                    col_40_sum = df.iloc[:, 40].sum()

                    if col_40_sum != 0:
                        calculated_data.append({
                            "product_id": "4 pins molex cable",
                            "qty_done": col_40_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })
                    col_42_sum = df.iloc[:, 42].sum()

                    if col_42_sum != 0:
                        calculated_data.append({
                            "product_id": "Front transparent window",
                            "qty_done": col_42_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })

                    col_48_sum = df.iloc[:, 48].sum()

                    if col_48_sum != 0:
                        calculated_data.append({
                            "product_id": "White plastic shell",
                            "qty_done": col_48_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })
                    col_49_sum = df.iloc[:, 49].sum()

                    if col_49_sum != 0:
                        calculated_data.append({
                            "product_id": "Back blue case",
                            "qty_done": col_49_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })

                    col_51_sum = df.iloc[:, 51].sum()

                    if col_51_sum != 0:
                        calculated_data.append({
                            "product_id": "Orange Pi Zero Thermal dissipator 14x14x6",
                            "qty_done": col_51_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })
                    col_52_sum = df.iloc[:, 52].sum()

                    if col_52_sum != 0:
                        calculated_data.append({
                            "product_id": "Power cable",
                            "qty_done": col_52_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })
                    col_53_sum = df.iloc[:, 53].sum()

                    if col_53_sum != 0:
                        calculated_data.append({
                            "product_id": "Ethernet molex cable",
                            "qty_done": col_53_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })
                    col_54_sum = df.iloc[:, 54].sum()

                    if col_54_sum != 0:
                        calculated_data.append({
                            "product_id": "OLED display",
                            "qty_done": col_54_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })

                    col_55_sum = df.iloc[:, 55].sum()

                    if col_55_sum != 0:
                        calculated_data.append({
                            "product_id": "Oled display filter",
                            "qty_done": col_55_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })

                    col_56_sum = df.iloc[:, 56].sum()

                    if col_56_sum != 0:
                        calculated_data.append({
                            "product_id": "Oled display mount",
                            "qty_done": col_56_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })

                    col_57_sum = df.iloc[:, 57].sum()

                    if col_57_sum != 0:
                        calculated_data.append({
                            "product_id": "Back blue case",
                            "qty_done": col_57_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })

                    col_58_sum = df.iloc[:, 58].sum()

                    if col_58_sum != 0:
                        calculated_data.append({
                            "product_id": "Front white case",
                            "qty_done": col_58_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })

                    col_60_sum = df.iloc[:, 60].sum()

                    if col_60_sum != 0:
                        calculated_data.append({
                            "product_id": "Back blue cover",
                            "qty_done": col_60_sum,
                            "location_id": "Joko Stock",
                            "location_dest_id": "Customers",
                            "product_uom_id": "Units",
                            "owner_id": "ECOJOKO",
                            "date": l2date,
                            "company": "ECOJOKO"
                        })







                except:
                    raise UserError(_("Invalid file!"))
        result_df = pd.DataFrame(calculated_data)
        result_df.to_excel("data.xlsx", index=False)
        df = pd.read_excel('data.xlsx')
        vals_list = []
        for _, row in df.iterrows():
            val = {}
            values = {}
            product = self.env['product.product'].search([('name', '=', str(row['product_id']))])
            if product:
                values.update({'product_id': product.id, })
            source = self.env['stock.location'].search([('name', '=', str(row['location_id']))])
            if source:
                values.update({'location_id': source.id, })
            owner = self.env['res.partner'].search([('name', '=', str(row['owner_id']))])
            if owner:
                values.update({'owner_id': owner.id, })

            values.update({'qty_done': float(row['qty_done'])})

            values.update({'date': row['date']})
            company = self.env['res.company'].search([('name', '=', str(row['company']))])
            if company:
                values.update({'company_id': company.id, })

            uom = self.env['uom.uom'].search([('name', '=', str(row['product_uom_id']))])
            if uom:
                values.update({'product_uom_id': uom.id, })
            dest = self.env['stock.location'].search([('name', '=', str(row['location_dest_id']))])
            if dest:
                values.update({'location_dest_id': dest.id, })
                print("Here is the id: ", dest.id)

            vals_list.append(values)
            print("This is the list", vals_list)

        if len(vals_list) != 0:
            url = 'http://localhost:8016'
            db = 'TestEcojoko'
            username = 'admin'
            password = 'admin'
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})

            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            # created_id = models.execute_kw(db, uid, password, 'stock.move.line', 'create', [vals_list])
            # self.write({'move_ids_without_package': created_id})
            print("Here is the list 2:", vals_list)
            return vals_list
        else:
            raise UserError("Invalid file type!")

    def rma_inventory(self):
        vals_list = self.import_rma_inventory()
        print("Here is the second list", vals_list)
        for val in vals_list:
            print("This is the val:", val)
            self.env['stock.move.line'].create({
                'picking_id': self.id,
                'product_id': val.get('product_id'),
                'company_id': val.get('company_id'),
                'product_uom_id': val.get('product_uom_id'),
                'lot_id': val.get('lot_id'),
                'qty_done': val.get('qty_done'),
                'location_id': val.get('location_id'),
                'location_dest_id': val.get('location_dest_id'),
                'lot_name': val.get('lot_name'),
                'owner_id': val.get('owner_id'),
            })

# This part is for importing customer returns
#The user needs to import a csv file in odoo and then the code will fill up the lines automatically

    def import_customer_returns(self):
        for data_file in self.upload_operations:
            file_name = data_file.name.lower()
            print(file_name)
            # if file_name.strip().endswith('.xlsx'):
            if file_name.strip().endswith('.csv'):
                try:
                    # fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                    fp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
                    fp.write(binascii.a2b_base64(data_file.datas))
                    fp.seek(0)
                    # df = pd.read_excel(fp.name, header=0, skiprows=0, usecols=range(24, 28))
                    df = pd.read_csv(fp.name)
                    seconds = (float(2 - 2 - 2023) - 25569) * 86400.0
                    l2date = datetime.utcfromtimestamp(seconds)
                except:
                    raise UserError(_("Invalid file!"))
        vals_list = []
        for _, row in df.iterrows():
            val = {}
            values = {}
            product = self.env['product.product'].search([('name', '=', str('Monky Pack'))])
            if product:
                values.update({'product_id': product.id, })
            source = self.env['stock.location'].search([('name', '=', str('Customers'))])
            if source:
                values.update({'location_id': source.id, })
            owner = self.env['res.partner'].search([('name', '=', str('ECOJOKO'))])
            if owner:
                values.update({'owner_id': owner.id, })

            values.update({'qty_done': float(1)})

            values.update({'date': l2date})
            company = self.env['res.company'].search([('name', '=', str('ECOJOKO'))])
            if company:
                values.update({'company_id': company.id, })

            uom = self.env['uom.uom'].search([('name', '=', str('Units'))])
            if uom:
                values.update({'product_uom_id': uom.id, })
            dest = self.env['stock.location'].search([('name', '=', str('Customer Returns'))])
            if dest:
                values.update({'location_dest_id': dest.id, })
                print("Here is the id: ", dest.id)

            serial = self.env['stock.lot'].search([('name', '=', str(row['serial number']))])
            if serial:
                values.update({'lot_id': serial.id, })

            vals_list.append(values)

        if len(vals_list) != 0:
            url = 'http://localhost:8016'
            db = 'TestEcojoko'
            username = 'admin'
            password = 'admin'
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})

            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            # created_id = models.execute_kw(db, uid, password, 'stock.move.line', 'create', [vals_list])
            # self.write({'move_ids_without_package': created_id})
            print("Here is the list 2:", vals_list)
            return vals_list
        else:
            raise UserError("Invalid file type!")

    def customer_returns(self):
        vals_list = self.import_customer_returns()
        print("This is the list",vals_list)
        for val in vals_list:
            self.env['stock.move.line'].create({
                'picking_id': self.id,
                'product_id': val.get('product_id'),
                'company_id': val.get('company_id'),
                'product_uom_id': val.get('product_uom_id'),
                'lot_id': val.get('lot_id'),
                'qty_done': val.get('qty_done'),
                'location_id': val.get('location_id'),
                'location_dest_id': val.get('location_dest_id'),
                'lot_name': val.get('lot_name'),
                'owner_id': val.get('owner_id'),
            })



# This part is for importing sympl data



    def import_sympl():
        print("true")




















