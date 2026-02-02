<?php
/**
 * Plugin Name: NCT Discount Banner
 * Description: Displays a discount banner and popup for WooCommerce
 * Version: 1.2
 * Author: Your Name
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

class NCT_Discount {

    private $coupon_code = 'NCT10';

    public function __construct() {
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('wp_footer', array($this, 'render_banner_and_popup'));
        add_action('wp_ajax_apply_nct_discount', array($this, 'apply_discount'));
        add_action('wp_ajax_nopriv_apply_nct_discount', array($this, 'apply_discount'));
    }

    public function enqueue_scripts() {
        wp_enqueue_style('nct-discount-styles', plugin_dir_url(__FILE__) . 'css/styles.css', array(), '1.2');
        wp_enqueue_script('nct-discount-script', plugin_dir_url(__FILE__) . 'js/script.js', array('jquery'), '1.2', true);

        wp_localize_script('nct-discount-script', 'nctDiscountAjax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('nct_discount_nonce')
        ));
    }
    
    public function render_banner_and_popup() {
        // Only show on frontend
        if (is_admin()) {
            return;
        }
        
        include plugin_dir_path(__FILE__) . 'templates/banner-popup.php';
    }
    
    public function apply_discount() {
        check_ajax_referer('nct_discount_nonce', 'nonce');

        if (!class_exists('WooCommerce')) {
            wp_send_json_error(array('message' => 'WooCommerce is not active'));
            return;
        }

        // Check if coupon exists
        $coupon = new WC_Coupon($this->coupon_code);

        if (!$coupon->get_id()) {
            wp_send_json_error(array('message' => 'Coupon does not exist'));
            return;
        }

        // Apply coupon to cart
        if (WC()->cart) {
            $applied = WC()->cart->apply_coupon($this->coupon_code);

            if ($applied) {
                wp_send_json_success(array(
                    'message' => 'Discount applied!',
                    'coupon_code' => $this->coupon_code
                ));
            } else {
                $error_message = 'Could not apply discount';
                // Get the last error from WooCommerce
                $notices = wc_get_notices('error');
                if (!empty($notices)) {
                    $error_message = strip_tags($notices[0]['notice']);
                    wc_clear_notices();
                }
                wp_send_json_error(array('message' => $error_message));
            }
        } else {
            wp_send_json_error(array('message' => 'Cart not available'));
        }
    }
}

// Initialize the plugin
new NCT_Discount();
