<?php
/**
 * Truck simulator markup: the controllable trucks in a yard with pallets to move. Used on the simulator page
 * and by [nct_truck_simulator].
 *
 * @var string $nctf_classes Extra classes for the wrapper.
 * @var string $nctf_place   'top' to move the block to the top of the page's main area, '' to leave it where it is output.
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<section id="nctf" class="nctf-sim <?php echo esc_attr( $nctf_classes ); ?>" data-place="<?php echo esc_attr( $nctf_place ); ?>" aria-label="<?php esc_attr_e( 'Truck simulator', 'nct-truck-finder' ); ?>">
<div class="nctf-sim-head">
  <div class="nctf-sim-title">
    <h1 class="nctf-title">Truck simulator</h1>
    <p class="nctf-lede">Pick a truck, drive it round the yard and move the pallets into the orange bays or the free rack positions.</p>
  </div>
  <div class="nctf-sim-task">
    <p class="nctf-task" id="nctf-task" role="status">Loading the yard</p>
    <button type="button" class="nctf-ctl" id="nctf-reset-yard">Reset the yard</button>
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
<div class="nctf-stage" id="nctf-stage">
    <canvas id="nctf-yard" role="img" tabindex="0" aria-label="3D model of the selected truck"></canvas>
    <p class="nctf-hint" id="nctf-hint" role="status"></p>
    <p class="nctf-stage-note" id="nctf-stage-note">Drag the view to look round. Arrow keys also drive.</p>
    <div class="nctf-stage-step" id="nctf-stage-step">
      <button type="button" class="nctf-ctl" id="nctf-zoom-out" aria-label="Zoom out"><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"></path></svg></button>
      <button type="button" class="nctf-ctl" id="nctf-zoom-in" aria-label="Zoom in"><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5v14"></path></svg></button>
      <button type="button" class="nctf-ctl" id="nctf-prev" aria-label="Previous truck"><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M15 5l-7 7 7 7"></path></svg></button>
      <span class="nctf-count" id="nctf-count">1 of 12</span>
      <button type="button" class="nctf-ctl" id="nctf-next" aria-label="Next truck"><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 5l7 7-7 7"></path></svg></button>
    </div>
    <div class="nctf-controls" id="nctf-controls" role="group" aria-label="Machine controls">
      <div class="nctf-dash-drive" id="nctf-drive">
        <div class="nctf-ped" id="nctf-ped" hidden>
          <div class="nctf-tiller" id="nctf-tiller" role="slider" tabindex="0" aria-label="Tiller arm: swing left or right to steer" aria-valuemin="-100" aria-valuemax="100" aria-valuenow="0">
            <svg viewBox="0 0 124 104" aria-hidden="true">
              <path d="M22 96 A44 44 0 0 1 102 96" fill="none" stroke="#7A3F77" stroke-width="2" stroke-dasharray="3 5"></path>
              <g id="nctf-tiller-g">
                <path d="M62 94 L62 34" stroke="#221a22" stroke-width="10" stroke-linecap="round"></path>
                <path d="M62 94 L62 34" stroke="#3a363d" stroke-width="2"></path>
                <rect x="34" y="12" width="56" height="24" rx="12" fill="#0e0d0f" stroke="#FB8E28" stroke-width="2"></rect>
                <rect x="24" y="17" width="14" height="14" rx="5" fill="#221a22" stroke="#9a9ca3" stroke-width="1.5"></rect>
                <rect x="86" y="17" width="14" height="14" rx="5" fill="#221a22" stroke="#9a9ca3" stroke-width="1.5"></rect>
                <circle cx="62" cy="24" r="6" fill="#E4125D"></circle>
              </g>
              <circle cx="62" cy="94" r="8" fill="#221a22" stroke="#FB8E28" stroke-width="2"></circle>
            </svg>
          </div>
          <div class="nctf-hlever"><div class="nctf-slot nctf-thr" id="nctf-throttle" role="slider" tabindex="0" aria-label="Travel control: push up to go forward, pull down to reverse" aria-valuemin="-100" aria-valuemax="100" aria-valuenow="0"><span class="nctf-knob"></span></div><span class="nctf-hl-name" id="nctf-throttle-name">Travel</span><span class="nctf-hl-val">hold to move</span></div>
        </div>
        <div class="nctf-rider" id="nctf-rider">
        <div class="nctf-wheel" id="nctf-wheel" role="slider" tabindex="0" aria-label="Steering wheel" aria-valuemin="-100" aria-valuemax="100" aria-valuenow="0">
          <svg viewBox="0 0 104 104" aria-hidden="true"><g id="nctf-wheel-g">
            <circle cx="52" cy="52" r="44" fill="none" stroke="#0e0d0f" stroke-width="12"></circle>
            <circle cx="52" cy="52" r="44" fill="none" stroke="#3a363d" stroke-width="2"></circle>
            <path d="M52 52 L52 12 M52 52 L18 72 M52 52 L86 72" stroke="#221a22" stroke-width="9" stroke-linecap="round"></path>
            <circle cx="52" cy="52" r="13" fill="#221a22" stroke="#FB8E28" stroke-width="2"></circle>
            <circle cx="21" cy="21" r="8" fill="#0e0d0f" stroke="#FB8E28" stroke-width="2"></circle>
          </g></svg>
        </div>
        <div class="nctf-dir" role="group" aria-label="Direction">
          <button type="button" id="nctf-dir-f" aria-pressed="true" aria-label="Forward">F</button>
          <button type="button" id="nctf-dir-n" aria-pressed="false" aria-label="Neutral">N</button>
          <button type="button" id="nctf-dir-r" aria-pressed="false" aria-label="Reverse">R</button>
        </div>
        <button type="button" class="nctf-pedal" id="nctf-pedal" aria-label="Accelerator pedal: hold to drive">Pedal</button>
        </div>
        <div class="nctf-gauge"><span>Speed</span><b id="nctf-speed">0.0</b><span>mph</span></div>
      </div>
      <div class="nctf-levers" id="nctf-levers">
        <div class="nctf-hlever"><div class="nctf-slot" id="nctf-lever-0" role="slider" tabindex="0" aria-label="Lift" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span class="nctf-knob"></span></div><span class="nctf-hl-name">Lift</span><span class="nctf-hl-val" id="nctf-lever-0-out">0%</span></div>
      </div>
      <div class="nctf-dash-end"><button type="button" class="nctf-ctl" id="nctf-park">Recover truck</button></div>
    </div>
</div>
<div class="nctf-sim-info" aria-live="polite">
  <div class="nctf-sim-info-main">
    <h2 id="nctf-t-name">Counterbalance</h2>
    <p class="nctf-aka" id="nctf-t-aka">The standard forklift</p>
    <p class="nctf-where" id="nctf-t-where"><b>Where you see it:</b> loading bays, yards and warehouses with wide aisles.</p>
  </div>
  <ul class="nctf-spot" id="nctf-t-spot">
    <li>Forks stick straight out at the front</li>
    <li>Heavy counterweight at the back, no legs in front</li>
    <li>Driver sits facing forwards under a cage</li>
  </ul>
  <div class="nctf-actions">
    <a class="nctf-btn nctf-btn-primary" href="<?php echo esc_url( home_url( '/courses/rtitb-counterbalance-courses/' ) ); ?>" id="nctf-t-link">See RTITB Counterbalance courses</a>
    <span class="nctf-callus">This is a simplified model for getting a feel for each truck. It is not operator training. Call <a href="tel:02030264629"><b>020 3026 4629</b></a> to book the real thing.</span>
  </div>
</div>
</section>
