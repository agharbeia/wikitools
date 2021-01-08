<?php
#   This script invokes the correct LocalSettings file of the intended wiki,
#+ based on its name. This file should be named "LocalSettings.php",
#+ and be located where its nameskae would normally be; probably via
#+ a symbolic link to its original location.
#   Wiki-specific configuraton files should be kept in their respective www directories.
if ( !defined( 'MEDIAWIKI' ) ) {
	exit;
} # Protect against web entry

$WebRoot = "/srv/www/wikido.xyz/";

if ( defined( 'MW_DB' ) ) {
    // Command-line mode and maintenance scripts (e.g. update.php) 
    $wikiname = substr(MW_DB, 0, -5);
    require_once ($WebRoot . $wikiname . "/LocalSettings.php");
} else {
    // Assume it being a web request
	if ( array_key_exists('SERVER_NAME', $_SERVER) ) {
	    $server = $_SERVER['SERVER_NAME'];
	    if ( preg_match( '/^(.*)\.wikido.xyz$/', $server, $matches ) ) {
    	    $wikiname = $matches[1];
	    } else {
    	    die( "We should not be here since Apache shouldn't have routed a request to $server to WikiDo." );
    	}
	} else {
		die("Couldn't guess which WikiDo member to work on.");
	}
    require_once ($WebRoot . $wikiname . "/LocalSettings.php");
}

## Global directives
//$wgReadOnly = 'الويكي في طور الصيانة. يمكنكم القراءة لكن لا يمكنكم التأليف.';
