// Copyright (c) 2026, Chetan Nahar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Office Expense", {
	refresh(frm) {
		if (frm.doc.docstatus === 1) {
			if (frm.doc.paid_from_employee_advance && frm.doc.employee_advances) {
				frm.dashboard.add_comment(
					__(
						"<strong>Note : </strong>If you want to cancel this expense, please do it from the linked <a href='/app/employee-advances/" + frm.doc.employee_advances + "'>Employee Advance</a>.",),
					"red",
					true
				);
				frm.page.btn_secondary.hide()
			} else {
				frm.page.btn_secondary.show()
			}
		}
	},
});


frappe.ui.form.on('MultiPayment Childtable for Expense', {
	mode_of_payment(frm, cdt, cdn) {

		let row = locals[cdt][cdn];

		// calculate total expense amount
		let total_amount = 0;
		(frm.doc.multi_expense || []).forEach(exp => {
			total_amount += flt(exp.amount);
		});

		if (!total_amount) return;

		// find row index
		let row_index = frm.doc.payment.findIndex(r => r.name === row.name);

		// if first row → full amount
		if (row_index === 0) {

			row.amount = total_amount;

		} else {

			// sum previous payment rows
			let paid_amount = 0;

			frm.doc.payment.forEach((p, i) => {
				if (i < row_index) {
					paid_amount += flt(p.amount);
				}
			});

			row.amount = total_amount - paid_amount;

			if (row.amount < 0) {
				row.amount = 0;
			}
		}

		frm.refresh_field("payment");
	},
});