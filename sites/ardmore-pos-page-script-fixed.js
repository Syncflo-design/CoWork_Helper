// FIXED script for Page doc "point-of-sale" on ardmoreceramics.c.frappe.cloud
// ---------------------------------------------------------------------------
// WHY: the custom sales-rep block Paul appended to this standard Page doc does
//   $('span[class="indicator-pill ..."]')[i].style.marginRight = "10px"
// inside a loop over ALL div.page-title elements on the desk. When another desk
// page (nest-home) has a page-title without a matching indicator-pill span, [i]
// is undefined -> TypeError. The crash fires around Recent-Orders interactions
// and intermittently kills the POS past-order summary panel, so users cannot
// reach the Return button. It also used innerHTML += which destroys event
// listeners inside the page title.
//
// FIX (lines inside setTimeout): scope to the POS page only, guard both element
// lookups, use insertAdjacentHTML, and dedupe on #salesrep.
//
// HOW TO APPLY (Administrator only - "Only Administrator can edit"):
//   Frappe Cloud dashboard -> ardmoreceramics site -> Login as Administrator
//   -> /app/page/point-of-sale -> replace the Script field with this file's
//   content -> Save -> hard-refresh the POS on a till.
// ---------------------------------------------------------------------------

frappe.provide("erpnext.PointOfSale");

frappe.pages["point-of-sale"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Point of Sale"),
		single_column: true,
		hide_sidebar: true,
	});

	frappe.require("point-of-sale.bundle.js", function () {
		wrapper.pos = new erpnext.PointOfSale.Controller(wrapper);
		window.cur_pos = wrapper.pos;
	});
};

frappe.pages["point-of-sale"].refresh = function (wrapper) {
	if (document.scannerDetectionData) {
		onScan.detachFrom(document);
		wrapper.pos.wrapper.html("");
		wrapper.pos.check_opening_entry();
	}
};


//# sourceURL=point_of_sale.js



$(document).ready(function () {

    let interval = setInterval(() => {

        if (cur_frm && cur_frm.doc && frappe && cur_pos) {
            console.log("Custom POS logic loaded!!");

                let options = '';
                let salesrep = '';
                cur_frm.changeSalesRep = function(value){
                    cur_frm.doc.custom_sales_representative = value;
                }
                frappe.call({
                    method: "server_scripts.public.py.pos.get_sales_reps",
                    args:{
                        'pos_profile': cur_pos.pos_profile
                    },
                    callback: function(r) {
                        if (r.message) {
                            r.message.forEach(name => {
                                options+=`<option value='${name.user}'>${name.user}</option>`
                            });
                            salesrep = `<select type="text"  onchange="cur_frm.changeSalesRep(this.value)" autocomplete="off" class="input-with-feedback form-control ellipsis bold" maxlength="140" style="width:200px" id="salesrep">
                            <option>Select POS User</option>
                            ${options}
                            </select>`;
                            setTimeout(function(){
                                var title = document.querySelector('#page-point-of-sale div.page-title');
                                if (title && !title.querySelector('#salesrep')) {
                                    title.insertAdjacentHTML('beforeend', salesrep);
                                    var pill = title.querySelector('span.indicator-pill');
                                    if (pill) pill.style.marginRight = "10px";
                                }
                            },500)

                        }

                    }
                });


            clearInterval(interval);

        }
    }, 1);
});
