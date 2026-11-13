<?php
/**
 * Plugin Name: NCT Hero 3D
 * Description: Replaces the flat illustrations in the homepage hero with 3D scenes on a turntable, one per training area. Nothing else in the hero changes, and the original illustrations remain as the fallback.
 * Version: 1.0.0
 * Author: National Compliance Training
 * Text Domain: nct-hero-3d
 * Requires at least: 5.8
 * Requires PHP: 7.2
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class NCT_Hero_3D {

	const VERSION = '1.0.0';

	public function __construct() {
		add_action( 'wp_enqueue_scripts', array( $this, 'enqueue' ) );
	}

	/**
	 * The 3D stage loads on the site's front page only.
	 * Change with:  add_filter( 'nct_hero_3d_enabled', '__return_false' );
	 */
	public function enqueue() {
		if ( is_admin() || ! apply_filters( 'nct_hero_3d_enabled', is_front_page() ) ) {
			return;
		}

		$url = plugin_dir_url( __FILE__ ) . 'assets/';

		wp_enqueue_style( 'nct-hero-3d', $url . 'css/hero3d.css', array(), self::VERSION );
		wp_enqueue_script( 'nct-hero-3d-three', $url . 'js/three.min.js', array(), 'r128', true );
		wp_enqueue_script( 'nct-hero-3d-gltf', $url . 'js/GLTFLoader.js', array( 'nct-hero-3d-three' ), 'r128', true );
		wp_enqueue_script( 'nct-hero-3d', $url . 'js/hero3d.js', array( 'nct-hero-3d-gltf' ), self::VERSION, true );
		wp_localize_script(
			'nct-hero-3d',
			'NCTHero3D',
			array(
				'models' => $url . 'models/',
				'ext'    => '.glb',
			)
		);
	}
}

new NCT_Hero_3D();
