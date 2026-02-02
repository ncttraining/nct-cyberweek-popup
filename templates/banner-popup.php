<div id="cw-banner" class="cw-banner">
    <div class="cw-banner-content">
        <span class="cw-banner-text">Get 10% OFF All Products!</span>
        <?php if (!is_user_logged_in()) : ?>
        <button id="cw-banner-btn" class="cw-banner-btn">Shop Now</button>
        <?php endif; ?>
    </div>
</div>

<?php if (!is_user_logged_in()) : ?>
<div id="cw-popup-overlay" class="cw-popup-overlay">
    <div class="cw-popup">
        <button class="cw-popup-close">&times;</button>
        <div class="cw-popup-content">
            <h2>Special Offer!</h2>
            <p class="cw-popup-subtitle">Exclusive Discount</p>
            <div class="cw-discount-badge">
                <span class="cw-discount-percent">10%</span>
                <span class="cw-discount-text">OFF</span>
            </div>
            <p class="cw-popup-description">Use code <strong>NCT10</strong> at checkout</p>
            <button id="cw-apply-discount" class="cw-apply-btn">APPLY DISCOUNT NOW</button>
            <p class="cw-popup-terms">*Valid on all products. Does not include examination resits.</p>
        </div>
    </div>
</div>
<?php endif; ?>
