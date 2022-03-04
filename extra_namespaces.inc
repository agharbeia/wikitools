<?php
declare(strict_types=1);

define("NS_FEATURE_CONTENT", 2);
define("NS_FEATURE_SUBPAGES", 4);
define("NS_FEATURE_SEARCHED", 8);
define("NS_FEATURE_SEMANTIC", 16);
define("TALK_PREFIX", "نقاش_");

function agh_define_namespace (string $name, int $id, ?int $properties = 0, ?string $contentModel = NULL, ?string $contentModel_talk = NULL, ?array $aliases = NULL) : void {

	global $wgExtraNamespaces, $wgContentNamespaces, $wgNamespacesWithSubpages, $wgNamespacesToBeSearchedDefault, $smwgNamespacesWithSemanticLinks, $wgNamespaceContentModels, $wgNamespaceAliases;

	$id_talk = $id + 1;

	$wgExtraNamespaces[$id] = $name;
	$wgExtraNamespaces[$id_talk] = TALK_PREFIX . $name;
	if (isset($properties)) {
		if ($properties & NS_FEATURE_CONTENT) $wgContentNamespaces[] = $id;
		if ($properties & NS_FEATURE_SUBPAGES) $wgNamespacesWithSubpages[$id] = TRUE;
		if ($properties & NS_FEATURE_SEARCHED) $wgNamespacesToBeSearchedDefault[$id] = TRUE;
		if ($properties & NS_FEATURE_SEMANTIC) $smwgNamespacesWithSemanticLinks[$id] = TRUE;
	}
	if (isset($contentModel)) $wgNamespaceContentModels[$id] = $contentModel;
	if (isset($contentModel_talk)) $wgNamespaceContentModels[$id_talk] = $contentModel_talk;
	if (isset($aliases)) foreach($aliases as $alias) $wgNamespaceAliases[$alias] = $id;
}
