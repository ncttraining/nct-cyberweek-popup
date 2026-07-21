jQuery(document).ready(function($) {

    // Check if popup has been shown in this session
    const popupShown = sessionStorage.getItem('cw_popup_shown');

    let lastFocused = null;

    function openPopup() {
        lastFocused = document.activeElement;
        $('#cw-popup-overlay').addClass('active');
        sessionStorage.setItem('cw_popup_shown', 'true');
        $('.cw-popup-close').trigger('focus');
    }

    function closePopup() {
        $('#cw-popup-overlay').removeClass('active');
        if (lastFocused && document.contains(lastFocused)) {
            lastFocused.focus();
        }
        lastFocused = null;
    }

    // Show popup on banner button click
    $('#cw-banner-btn').on('click', function() {
        openPopup();
    });

    // Show popup automatically if not shown yet (optional)
    if (!popupShown) {
        setTimeout(function() {
            openPopup();
        }, 3000); // Show after 3 seconds
    }

    // Close popup when clicking X button
    $('.cw-popup-close').on('click', function() {
        closePopup();
    });

    // Close popup when clicking outside the popup
    $('#cw-popup-overlay').on('click', function(e) {
        if (e.target === this) {
            closePopup();
        }
    });

    // Close popup on ESC key
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape' && $('#cw-popup-overlay').hasClass('active')) {
            closePopup();
        }
    });

    // Keep keyboard focus inside the dialog while it is open
    $(document).on('keydown', function(e) {
        if (e.key !== 'Tab' || !$('#cw-popup-overlay').hasClass('active')) {
            return;
        }
        const focusable = $('#cw-popup-overlay').find('button:not(:disabled)');
        if (!focusable.length) {
            return;
        }
        const first = focusable.first()[0];
        const last = focusable.last()[0];
        if (e.shiftKey && document.activeElement === first) {
            e.preventDefault();
            last.focus();
        } else if (!e.shiftKey && (document.activeElement === last || !$.contains($('#cw-popup-overlay')[0], document.activeElement))) {
            e.preventDefault();
            first.focus();
        }
    });

    // Apply discount
    $('#cw-apply-discount').on('click', function() {
        const $button = $(this);
        const originalText = $button.text();

        // Disable button and show loading state
        $button.prop('disabled', true).text('Applying...');

        $.ajax({
            url: nctDiscountAjax.ajax_url,
            type: 'POST',
            data: {
                action: 'apply_nct_discount',
                nonce: nctDiscountAjax.nonce
            },
            success: function(response) {
                if (response.success) {
                    $button.text('✓ Discount Applied!');

                    // Close popup after 1.5 seconds
                    setTimeout(function() {
                        closePopup();
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
