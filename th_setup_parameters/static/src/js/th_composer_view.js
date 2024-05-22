/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { PyDateTime } from "@web/core/py_js/py_date";

const modelList = ["prm.lead","th.apm", "pom.lead", "crm.lead", "ccs.lead","th.student"]

registerPatch({
    name: 'ComposerView',
    recordMethods: {
        /**
         * @override
         */
        onClickSend() {
            this._super.apply(this, arguments);
            if (modelList.includes(this.chatter.webRecord.resModel)){
                this.env.services.orm.write(this.chatter.webRecord.resModel, [this.chatter.webRecord.resId], { th_last_check: PyDateTime.now().strftime("%Y-%m-%d %H:%M:%S")})
            }
            this.chatter.webRecord.load()
        },
    },
});
