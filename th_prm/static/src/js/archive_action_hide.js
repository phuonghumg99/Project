/** @odoo-module */

import { registry } from '@web/core/registry';
import { formView } from '@web/views/form/form_view';
import { FormController } from "@web/views/form/form_controller";


export class CustomPrmFormController extends FormController {
    async setup() {
        super.setup()
        this.archiveEnabled = false;
    }
}

registry.category('views').add('custom_prm_form', {
    ...formView,
    Controller: CustomPrmFormController,
});