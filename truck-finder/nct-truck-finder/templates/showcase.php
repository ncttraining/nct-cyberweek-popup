<?php
/**
 * Truck finder markup, showcase view (turntable display, no driving controls).
 *
 * @var string $nctf_classes Extra classes for the wrapper.
 * @var string $nctf_place   'top' to move the block to the top of the page's main area, '' to leave it where it is output.
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<section id="nctf" class="nctf-showcase <?php echo esc_attr( $nctf_classes ); ?>" data-place="<?php echo esc_attr( $nctf_place ); ?>" aria-label="<?php esc_attr_e( 'Truck finder', 'nct-truck-finder' ); ?>">
<div class="nctf-hero-in">
  <div class="nctf-intro">
    <h2 class="nctf-title">Which truck do you need training on?</h2>
    <p class="nctf-lede">Pick the one that looks like yours. We train operators on all of them, on-site or at our Nuneaton centre.</p>
  </div>

  <div class="nctf-stage" id="nctf-stage">
    <canvas id="nctf-yard" role="img" tabindex="0" aria-label="3D model of the selected truck"></canvas>
    <p class="nctf-stage-note" id="nctf-stage-note">Drag to turn the truck</p>
    <div class="nctf-stage-step" id="nctf-stage-step">
      <button type="button" class="nctf-ctl" id="nctf-prev" aria-label="Previous truck"><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M15 5l-7 7 7 7"></path></svg></button>
      <span class="nctf-count" id="nctf-count">1 of 12</span>
      <button type="button" class="nctf-ctl" id="nctf-next" aria-label="Next truck"><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 5l7 7-7 7"></path></svg></button>
    </div>
  </div>

  <div class="nctf-info" aria-live="polite">
    <div class="nctf-info-card">
      <div>
        <h2 id="nctf-t-name">Counterbalance</h2>
        <p class="nctf-aka" id="nctf-t-aka">The standard forklift</p>
      </div>
      <ul class="nctf-spot" id="nctf-t-spot">
        <li>Forks stick straight out at the front</li>
        <li>Heavy counterweight at the back, no legs in front</li>
        <li>Driver sits facing forwards under a cage</li>
      </ul>
      <p class="nctf-where" id="nctf-t-where"><b>Where you see it:</b> loading bays, yards and warehouses with wide aisles.</p>
      <div class="nctf-actions">
        <a class="nctf-btn nctf-btn-primary" href="<?php echo esc_url( home_url( '/courses/rtitb-counterbalance-courses/' ) ); ?>" id="nctf-t-link">See RTITB Counterbalance courses</a>
        <span class="nctf-callus">Still not sure? Call <a href="tel:02030264629"><b>020 3026 4629</b></a></span>
      </div>
    </div>
  </div>

  <div class="nctf-tabs" id="nctf-tabs" role="group" aria-label="Truck type">
    <button type="button" class="nctf-tab" aria-pressed="true">Counterbalance</button>
    <button type="button" class="nctf-tab" aria-pressed="false">Reach</button>
    <button type="button" class="nctf-tab" aria-pressed="false">Pivot Steer</button>
    <button type="button" class="nctf-tab" aria-pressed="false">VNA</button>
    <button type="button" class="nctf-tab" aria-pressed="false">Telehandler</button>
    <button type="button" class="nctf-tab" aria-pressed="false">Powered pallet truck</button>
    <button type="button" class="nctf-tab" aria-pressed="false">Pump truck</button>
    <button type="button" class="nctf-tab" aria-pressed="false">Order picker, low level</button>
    <button type="button" class="nctf-tab" aria-pressed="false">Order picker, high level</button>
    <button type="button" class="nctf-tab" aria-pressed="false">MEWP scissor lift</button>
    <button type="button" class="nctf-tab" aria-pressed="false">MEWP boom lift</button>
    <button type="button" class="nctf-tab" aria-pressed="false">Gantry crane</button>
  </div>
</div>
</section>
