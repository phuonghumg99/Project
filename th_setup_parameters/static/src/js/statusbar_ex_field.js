/** @odoo-module **/

import { registry } from '@web/core/registry';
import { StatusBarField } from '@web/views/fields/statusbar/statusbar_field';
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { useAutofocus, useBus, useService } from "@web/core/utils/hooks";



class ThStatusbarField extends StatusBarField {
    setup(){
        super.setup()
        this.dialog = useService("dialog");
    }
    selectItem(Item) {
        this.dialog.add(ConfirmationDialog, {
                title: "Xác nhận!",
                body: "Bạn có muốn chuyển đổi trạng thái?",
                confirm: async () => super.selectItem(Item),
                cancel: () => {},
            });
    }
}

registry.category("fields").add("th_statusbar", ThStatusbarField)