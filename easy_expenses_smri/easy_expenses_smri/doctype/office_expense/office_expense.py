# Copyright (c) 2026, Chetan Nahar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OfficeExpense(Document):
	def before_save(doc):
		# firstly check if total amount payment = total amount of expense
		if sum([each_exp.get('amount') for each_exp in doc.multi_expense]) != sum([each_pay.get('amount') for each_pay in doc.payment]):
			frappe.throw('Total payments do not match total expenses.')
		doc.amount = sum([each_exp.get('amount') for each_exp in doc.multi_expense])

	def before_submit(doc):
		# Validate mandatory fields
		if not doc.amount:
			frappe.throw("Amount is required before submission.")

		
		je = frappe.new_doc("Journal Entry")
		# je.custom_entry_for = "Expense"
		# je.custom_document_type = "Expense Entry"
		# je.custom_linked_document = doc.name
		je.voucher_type = "Journal Entry"
		je.posting_date = doc.posting_date
		je.user_remark = ', '.join([f"{each_exp.get('expense_category')} : Rs.{each_exp.get('amount')}" for each_exp in doc.multi_expense])
		je.user_remark += '\n'+(doc.additional_info if doc.additional_info else '')
		
		# First account - Assign Head (Debit)
		for each_exp in doc.multi_expense:
			exp_category_doc = frappe.get_doc('Expense Category', each_exp.get('expense_category'))
			expense_account = exp_category_doc.expense_head
			je.append("accounts", {
				"account": expense_account,
				"debit_in_account_currency": each_exp.get('amount'),
				"credit_in_account_currency": 0,
			})


		# Second account - Payment Method (Credit)
		for each_pay in doc.payment:
			mode_of_payment = frappe.get_doc("Mode of Payment", each_pay.get('mode_of_payment'))
			if not mode_of_payment.accounts:
				frappe.throw(f"No account found for Payment Method: {each_pay.get('mode_of_payment')}")
			payment_account = mode_of_payment.accounts[0].default_account
			je.append("accounts", {
				"account": payment_account,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": each_pay.get('amount'),
			})

		# Save the Journal Entry
		je.insert()
		je.submit()
		doc.journal_entry = je.name

	def on_cancel(doc):
		je_doc = frappe.get_doc('Journal Entry', doc.journal_entry)
		je_doc.cancel()

	def on_trash(doc):
		if doc.journal_entry:
			# Break link first
			frappe.db.set_value("Office Expense", doc.name, "journal_entry", None)

			# Commit so DB releases link
			frappe.db.commit()

			# Now delete
			delete_entry("Journal Entry", doc.journal_entry)


def delete_entry(doctype,name):
	doc = frappe.get_doc(doctype, name)
	doc.delete()
