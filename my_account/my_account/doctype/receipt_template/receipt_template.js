// Copyright (c) 2020, GMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Receipt Template', {
	subdomain: function(frm) {
			if (frm.doc.subdomain){

			frappe.call({
		        "method": "my_account.my_account.doctype.buy_new_user.buy_new_user.fetch_data_subdomain",
				args: {
					// doctype: "Master Subdomain",
					subdomain: frm.doc.subdomain
		        },
		        callback: function (data) {
		        	// console.log(data.message)
		        	frm.set_df_property("user", "read_only", 1)
					frm.set_value( "user",data.message[0])
					frm.set_value( "full_name",data.message[1])
		            
		        }
		    })	
			}
	}
});
