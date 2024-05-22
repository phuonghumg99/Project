/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _lt } from "@web/core/l10n/translation";
import { useInputField } from "@web/views/fields/input_field_hook";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

export class TreeUrlField extends Component {
    async setup() {
        useInputField({ getValue: () => this.props.value || "" });
    }

    get formattedHref() {
        let model = this.props.record.resModel
        let id = this.props.record.resId
        let url_origin = self.origin
        let get_menu = self.location.hash ? self.location && self.location.hash : ''
        let menu_xml = ''
        if (get_menu != '') {
            menu_xml = get_menu.split('&')[1]
        }
        let url = url_origin + '/web?#action='  + '&view_type=form&model=' + model + '&id=' + id.toString()
        let value = "";
        if (typeof this.props.value === "string") {
            const shouldaddPrefix = !(this.props.websitePath || this.props.value.includes("://") || /^\//.test(this.props.value));

            value = shouldaddPrefix ? url : this.props.value;
        }
        return value;
    }
}

TreeUrlField.template = "web.UrlField";
TreeUrlField.displayName = _lt("URL");
TreeUrlField.supportedTypes = ["char"];

TreeUrlField.props = {
    ...standardFieldProps,
    placeholder: { type: String, optional: true },
    text: { type: String, optional: true },
    websitePath: { type: Boolean, optional: true },
};

TreeUrlField.extractProps = ({ attrs }) => {
    return {
        text: attrs.text,
        websitePath: attrs.options.website_path,
        placeholder: attrs.placeholder,
    };
};


registry.category("fields").add("tree_url", TreeUrlField);
