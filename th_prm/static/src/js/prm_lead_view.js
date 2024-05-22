/** @odoo-module **/

import {registry} from '@web/core/registry';
import {listView} from '@web/views/list/list_view';
import {ListController} from '@web/views/list/list_controller';
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import rpc from 'web.rpc';

export class PrmListController extends ListController {
    async setup() {
        super.setup()
        this.archiveEnabled = false;
        this.isManager = await this.model.user.hasGroup("th_prm.group_prm_administrator");
    }


    async check_last_status(active_ids){
        const last_status = await rpc.query({
            model: this.model.root.resModel,
            method: 'check_last_status',
            args: [active_ids],
        });
        if (last_status) {
            this.dialogService.add(ConfirmationDialog, {
                title: "Cảnh báo!",
                body: "Không thể thu hồi về kho khi có bản ghi ở trạng thái P6 và đã tồn tại POM hoặc trạng thái C4.",
                confirm: async () => {},
                cancel: () => {},
            });
        }
        else {
            this.archiveActiveIds(active_ids)
        }

    }
    async archiveActiveIds(active_ids) {
        await rpc.query({
            model: this.model.root.resModel,
            method: 'th_action_archive',
            args: [active_ids],
        });
        this.model.load();
    }

    async onClickSettingDomainLead() {
        const activeIds = await this.getSelectedResIds()
        if (activeIds.length !== 0) {
            this.dialogService.add(ConfirmationDialog, {
                title: "Xác nhận thu hồi",
                body: "Bạn có chắc chắn muốn thu hồi về kho",
                confirm: async () => await this.check_last_status(activeIds),
                cancel: () => {},
            });
        }
    }
}

export const prmListView = {
    ...listView,
    Controller: PrmListController,
    buttonTemplate: "th_prm.PrmLeadListView.Buttons",
}

export class PrmListReuseController extends ListController {
    async setup() {
        super.setup()
        this.archiveEnabled = false;
        this.isManager = await this.model.user.hasGroup("th_prm.group_prm_administrator");
    }

    async onClickReuseLead() {
        const activeIds = await this.getSelectedResIds()
        if (activeIds.length !== 0) {
            var context = this.props.context
            context['active_ids'] = activeIds
            context['model_name'] = this.model.root.resModel
            this.actionService.doAction({
                name: "Cấu hình",
                type: "ir.actions.act_window",
                res_model: "prm.lead.reuse",
                target: "new",
                views: [[false, "form"]],
                context: context,
            });
        }
    }
}

export const prmListReuseView = {
    ...listView,
    Controller: PrmListReuseController,
    buttonTemplate: "th_prm.PrmLeadListReuseView.Buttons",
}

registry.category('views').add('prm_lead_list', prmListView);
registry.category('views').add('prm_lead_list_reuse', prmListReuseView);