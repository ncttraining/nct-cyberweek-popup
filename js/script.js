jQuery(document).ready(function($) {
    
    // Check if popup has been shown in this session
    const popupShown = sessionStorage.getItem('cw_popup_shown');
    
    // Show popup on banner button click
    $('#cw-banner-btn').on('click', function() {
        $('#cw-popup-overlay').addClass('active');
        sessionStorage.setItem('cw_popup_shown', 'true');
    });
    
    // Show popup automatically if not shown yet (optional)
    if (!popupShown) {
        setTimeout(function() {
            $('#cw-popup-overlay').addClass('active');
            sessionStorage.setItem('cw_popup_shown', 'true');
        }, 3000); // Show after 3 seconds
    }
    
    // Close popup when clicking X button
    $('.cw-popup-close').on('click', function() {
        $('#cw-popup-overlay').removeClass('active');
    });
    
    // Close popup when clicking outside the popup
    $('#cw-popup-overlay').on('click', function(e) {
        if (e.target === this) {
            $(this).removeClass('active');
        }
    });
    
    // Close popup on ESC key
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape') {
            $('#cw-popup-overlay').removeClass('active');
        }
    });
    
    // Apply discount
    $('#cw-apply-discount').on('click', function() {
        const $button = $(this);
        const originalText = $button.text();
        
        // Disable button and show loading state
        $button.prop('disabled', true).text('Applying...');
        
        $.ajax({
            url: winterSaleAjax.ajax_url,
            type: 'POST',
            data: {
                action: 'apply_winter_sale_discount',
                nonce: winterSaleAjax.nonce
            },
            success: function(response) {
                if (response.success) {
                    $button.text('✓ Discount Applied!');
                    
                    // Close popup after 1.5 seconds
                    setTimeout(function() {
                        $('#cw-popup-overlay').removeClass('active');
                        $button.text(originalText).prop('disabled', false);
                        
                        // Redirect to cart or reload page
                        if (typeof wc_add_to_cart_params !== 'undefined') {
                            window.location.href = wc_add_to_cart_params.cart_url;
                        } else {
                            location.reload();
                        }
                    }, 1500);
                } else {
                    alert(response.data.message || 'Could not apply discount. Please try again.');
                    $button.text(originalText).prop('disabled', false);
                }
            },
            error: function() {
                alert('An error occurred. Please try again.');
                $button.text(originalText).prop('disabled', false);
            }
        });
    });
    
});
