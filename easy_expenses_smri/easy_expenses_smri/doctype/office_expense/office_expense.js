// Copyright (c) 2026, Chetan Nahar and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Office Expense", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on('MultiPayment Childtable for Expense', {
	mode_of_payment(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		// Only run if first payment row
		if (frm.doc.payment && frm.doc.payment.length === 1) {
			let total_amount = 0;
			(frm.doc.multi_expense || []).forEach(row => {
				total_amount += flt(row.amount);
			});
			if (total_amount > 0) {
				row.amount = total_amount;
				frm.refresh_field("payment");
			}
		}
	},
});