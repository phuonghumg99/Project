/** @odoo-module **/

import field_registry from 'web.field_registry';
import "@mail/js/activity";
const KanbanActivity = field_registry.get('kanban_activity');

const modelList = ["prm.lead","th.apm", "pom.lead", "th.trm.lead", "crm.lead", "ccs.lead","th.student"]

KanbanActivity.include({
    async _markActivityDone(params) {
        this._super(...arguments);
        if (modelList.includes(this.model)) {
            this._rpc({
                model: this.model,
                method: 'update_th_last_check',
                args: [[this.res_id]],
            });
        }
    },

    async _markActivityDoneAndScheduleNext(params) {
        this._super(...arguments);
        if (modelList.includes(this.model)) {
            this._rpc({
                model: this.model,
                method: 'update_th_last_check',
                args: [[this.res_id]],
            });
        }
    },
});
