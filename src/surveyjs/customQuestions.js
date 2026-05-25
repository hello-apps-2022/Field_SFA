// SFA Mobile Renderer Mappings
// This file maps standard SurveyJS question types to mobile renderer components
// No custom question classes needed - SurveyJS Creator has all standard types built-in

// Standard SurveyJS question types available in Creator toolbox:
// text, checkbox, radiogroup, dropdown, comment, rating, ranking, imagepicker,
// boolean, expression, file, html, matrix, multipletext, panel, paneldynamic

// Mobile renderer mappings - tells the React Native app which component to use
export const mobileRenderers = {
    text: 'TextInputRenderer',
    checkbox: 'CheckboxRenderer',
    radiogroup: 'RadioGroupRenderer',
    dropdown: 'DropdownRenderer',
    comment: 'TextAreaRenderer',
    rating: 'RatingRenderer',
    ranking: 'RankingRenderer',
    imagepicker: 'ImagePickerRenderer',
    boolean: 'ToggleRenderer',
    expression: 'ExpressionRenderer',
    file: 'FileUploadRenderer',
    html: 'HtmlRenderer',
    matrix: 'MatrixRenderer',
    multipletext: 'MultiTextRenderer',
    panel: 'PanelRenderer',
    paneldynamic: 'DynamicPanelRenderer',
};

// SFA-specific field aliases - standard types with SFA-specific labels
// These are just label overrides, not new question types
export const sfaFieldAliases = {
    'Customer Photo': { type: 'file', maxSize: 2097152, acceptedTypes: 'image/*' },
    'GPS Location': { type: 'text', inputType: 'hidden', readOnly: true },
    'Signature': { type: 'text', inputType: 'hidden' },
    'SKU Quantity': { type: 'multipletext', items: [
        { name: 'carton', title: 'Carton Qty' },
        { name: 'free', title: 'Free Qty' },
        { name: 'unpaid', title: 'Unpaid Qty' }
    ]},
    'Barcode Scan': { type: 'text', placeholder: 'Scan or type barcode' },
};
