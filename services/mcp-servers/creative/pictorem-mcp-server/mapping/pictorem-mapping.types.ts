/**
 * Pictorem Site Mapping Interfaces
 * Auto-generated from site mapping on 2025-05-29T17:46:14.062Z
 * Authenticated mapping: true
 */

export interface PictoremSiteMapping {
  metadata: {
    mapped_date: string;
    site_url: string;
    mapper_version: string;
    authenticated: boolean;
  };
  authentication: {
    login_url?: string;
    email_field?: string;
    password_field?: string;
    submit_button?: string;
    success_indicator?: string;
  };
  upload_flow: {
    upload_url?: string;
    file_input?: string;
    dropzone?: string;
  };
  product_configuration: {
    product_type_selector?: string;
    product_types?: string[];
    width_selector?: string;
    height_selector?: string;
    size_selector?: string;
    canvas_type_selector?: string;
    canvas_types?: string[];
    frame_selector?: string;
    quantity_selector?: string;
  };
  pricing: {
    price_display?: string;
    add_to_cart_button?: string;
  };
  checkout_flow: {
    checkout_trigger?: string;
    checkout_url?: string;
    customer_fields?: FormFields;
    shipping_fields?: FormFields;
  };
  payment_methods: {
    payment_selector?: string;
    available_methods?: PaymentMethod[];
    card_fields?: FormFields;
    place_order_button?: string;
  };
  navigation: {
    [key: string]: string;
  };
  error_patterns: {
    [selector: string]: {
      selector: string;
      count: number;
      likely_error_container: boolean;
    };
  };
}

export interface FormFields {
  email?: string;
  password?: string;
  name?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  zip?: string;
  card_number?: string;
  expiry?: string;
  cvv?: string;
  card_name?: string;
}

export interface PaymentMethod {
  value?: string;
  label?: string;
}
