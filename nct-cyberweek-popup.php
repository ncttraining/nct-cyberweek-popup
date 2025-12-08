<?php
/**
 * Plugin Name: Cyber Week Discount Banner
 * Description: Displays a Cyber Week discount banner and popup for WooCommerce
 * Version: 1.1
 * Author: Your Name
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

class Cyber_Week_Discount {
    
    private $coupon_code = 'CYBERWEEK';
    
    public function __construct() {
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('wp_footer', array($this, 'render_banner_and_popup'));
        add_action('wp_ajax_apply_cyber_week_discount', array($this, 'apply_discount'));
        add_action('wp_ajax_nopriv_apply_cyber_week_discount', array($this, 'apply_discount'));
    }
    
    public function enqueue_scripts() {
        wp_enqueue_style('cyber-week-styles', plugin_dir_url(__FILE__) . 'css/styles.css', array(), '1.1');
        wp_enqueue_script('cyber-week-script', plugin_dir_url(__FILE__) . 'js/script.js', array('jquery'), '1.1', true);
        
        wp_localize_script('cyber-week-script', 'cyberWeekAjax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('cyber_week_nonce')
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
        check_ajax_referer('cyber_week_nonce', 'nonce');
        
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
                    'message' => 'Cyber Week discount applied!',
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
new Cyber_Week_Discount();
