/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { PyDateTime } from "@web/core/py_js/py_date";

const modelList = ["prm.lead","th.apm" ,"pom.lead", "crm.lead","th.trm.lead", "ccs.lead","th.student"]

function get_model_name() {
    let current_url = window.location.href.split("#")
    let current_url_array = current_url[1].split('&')
    for (let variable of current_url_array) {
        variable = variable.split('=')
        if (variable[0] === 'model') return variable[1]
    }
}

registerPatch({
    name: 'ActivityMarkDonePopoverContentView',
    recordMethods: {
        /**
         * @override
         */
        async onClickDone() {
            // const model_name = get_model_name();
            // if (!modelList.includes(model_name)) return;
            const chatter = this.activityViewOwner && this.activityViewOwner.activityBoxView.chatter;
            const webRecord = chatter ? chatter.webRecord : this.webRecord
            if (modelList.includes(webRecord.resModel)){
                this.env.services.orm.write(webRecord.resModel, [webRecord.resId], { th_last_check: PyDateTime.now().strftime("%Y-%m-%d %H:%M:%S")})
            }
            this._super.apply(this, arguments);
        },

        /**
         * @override
         */
        async onClickDoneAndScheduleNext() {
            // const model_name = get_model_name();
            // if (!modelList.includes(model_name)) return;
            const chatter = this.activityViewOwner && this.activityViewOwner.activityBoxView.chatter;
            const webRecord = chatter ? chatter.webRecord : this.webRecord
            if (modelList.includes(webRecord.resModel)){
                this.env.services.orm.write(webRecord.resModel, [webRecord.resId], { th_last_check: PyDateTime.now().strftime("%Y-%m-%d %H:%M:%S")})
            }
            this._super.apply(this, arguments);
        },
    },
});
