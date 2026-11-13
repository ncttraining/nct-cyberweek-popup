<?php
/**
 * Plugin Name: NCT Homepage Hero 3D
 * Description: Replaces the five flat illustrations in the homepage hero with 3D models on a turntable. The original illustrations stay in the page and show again if 3D is unavailable.
 * Version: 1.0.0
 * Author: National Compliance Training
 * Text Domain: nct-homepage-hero
 * Requires at least: 5.8
 * Requires PHP: 7.2
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class NCT_Homepage_Hero {

	const VERSION = '1.0.0';

	public function __construct() {
		add_action( 'wp_enqueue_scripts', array( $this, 'enqueue' ) );
	}

	/**
	 * Only the front page gets the 3D hero.
	 * Change with:  add_filter( 'nct_homepage_hero_enabled', '__return_false' );
	 */
	private function enabled() {
		return (bool) apply_filters( 'nct_homepage_hero_enabled', is_front_page() );
	}

	public function enqueue() {
		if ( ! $this->enabled() ) {
			return;
		}
		$url = plugin_dir_url( __FILE__ ) . 'assets/';

		wp_enqueue_style( 'nct-homepage-hero', $url . 'css/hero3d.css', array(), self::VERSION );

		// Everything loads in the footer, in this order: three.js, its loader, the stage element, the 3D scene,
		// then the link that keeps the scene in step with the theme's tabs.
		wp_enqueue_script( 'nct-homepage-hero-three', $url . 'js/three.min.js', array(), 'r128', true );
		wp_enqueue_script( 'nct-homepage-hero-gltf', $url . 'js/GLTFLoader.js', array( 'nct-homepage-hero-three' ), 'r128', true );
		wp_enqueue_script( 'nct-homepage-hero-stage', $url . 'js/hero3d-stage.js', array( 'nct-homepage-hero-gltf' ), self::VERSION, true );
		wp_enqueue_script( 'nct-homepage-hero', $url . 'js/hero3d.js', array( 'nct-homepage-hero-stage' ), self::VERSION, true );
		wp_enqueue_script( 'nct-homepage-hero-sync', $url . 'js/hero3d-sync.js', array( 'nct-homepage-hero' ), self::VERSION, true );
		wp_localize_script(
			'nct-homepage-hero-stage',
			'NCTHero3D',
			array(
				'models' => $url . 'models/',
				'ext'    => '.glb',
			)
		);
	}
}

new NCT_Homepage_Hero();
