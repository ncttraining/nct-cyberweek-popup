<?php
/**
 * Plugin Name: NCT Truck Finder
 * Description: Interactive 3D "Which truck do you need training on?" selector with working controls. Adds itself to the top of the forklift training page, and is available anywhere with the [nct_truck_finder] shortcode.
 * Version: 1.0.0
 * Author: National Compliance Training
 * Text Domain: nct-truck-finder
 * Requires at least: 5.8
 * Requires PHP: 7.2
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class NCT_Truck_Finder {

	const VERSION = '1.0.0';

	/** Only one finder can be on a page: its element ids are unique. */
	private $rendered = false;

	public function __construct() {
		add_action( 'wp_enqueue_scripts', array( $this, 'register_assets' ) );
		add_shortcode( 'nct_truck_finder', array( $this, 'shortcode' ) );
		add_filter( 'the_content', array( $this, 'auto_insert' ), 20 );
	}

	/**
	 * Page slugs (or IDs) that get the finder added to the top automatically.
	 * Change with:  add_filter( 'nct_truck_finder_auto_pages', function () { return array(); } );
	 */
	private function auto_pages() {
		return (array) apply_filters( 'nct_truck_finder_auto_pages', array( 'forklift-training' ) );
	}

	public function register_assets() {
		$url = plugin_dir_url( __FILE__ ) . 'assets/';
		wp_register_style( 'nct-truck-finder', $url . 'css/finder.css', array(), self::VERSION );
		wp_register_script( 'nct-truck-finder-three', $url . 'js/three.min.js', array(), 'r128', true );
		wp_register_script( 'nct-truck-finder-gltf', $url . 'js/GLTFLoader.js', array( 'nct-truck-finder-three' ), 'r128', true );
		wp_register_script( 'nct-truck-finder', $url . 'js/finder.js', array( 'nct-truck-finder-gltf' ), self::VERSION, true );
		wp_localize_script(
			'nct-truck-finder',
			'NCTTruckFinder',
			array(
				'models'  => $url . 'models/',
				'courses' => trailingslashit( home_url( '/courses' ) ),
			)
		);

		// Load the stylesheet in the head on pages that will show the finder, so it never appears unstyled.
		$pages = $this->auto_pages();
		if ( $pages && is_page( $pages ) ) {
			wp_enqueue_style( 'nct-truck-finder' );
		}
	}

	private function render( $place ) {
		if ( $this->rendered ) {
			return '';
		}
		$this->rendered = true;

		wp_enqueue_style( 'nct-truck-finder' );
		wp_enqueue_script( 'nct-truck-finder' );

		$nctf_place   = 'top' === $place ? 'top' : '';
		$nctf_classes = 'top' === $place ? 'nctf-breakout' : '';

		ob_start();
		include plugin_dir_path( __FILE__ ) . 'templates/finder.php';
		return ob_get_clean();
	}

	/** [nct_truck_finder] or [nct_truck_finder place="top"] */
	public function shortcode( $atts ) {
		$atts = shortcode_atts( array( 'place' => '' ), $atts, 'nct_truck_finder' );
		return $this->render( $atts['place'] );
	}

	/** Adds the finder to the top of the configured pages. */
	public function auto_insert( $content ) {
		if ( is_admin() || ! is_singular() || ! in_the_loop() || ! is_main_query() ) {
			return $content;
		}
		$pages = $this->auto_pages();
		if ( ! $pages || ! is_page( $pages ) ) {
			return $content;
		}
		if ( has_shortcode( $content, 'nct_truck_finder' ) || false !== strpos( $content, 'id="nctf"' ) ) {
			return $content;
		}
		return $this->render( 'top' ) . $content;
	}
}

new NCT_Truck_Finder();
