# wikitoolsp
A collection of tools to manage Mediawiki installations and wikifamilies; based on the specifics of WikiDo.XYZ

The scripts are buillts

* mw-getextensions.py : downloads MW extensions by name from the ExtensionDistributor.
* transmerge.py : a tool to help migrate forked localisation strings between upstream releases.
* LocalSettings-dispatcher.php : a LocalSettings.php to run a farm from the same code-base via cascading down to instance-specific LocalSettings.php's based on the name of each wiki.
* wiki-instance.sh :  a Bash shell script to instantiate wikis based on templates of configuraion files, and hooking them to the mechanics of a farm.
* templates/ :  a set of templates of configuration files for a wiki instance. Including: LocalSettings.php, Apache configuration, database schema, and otherswiki-instance.shwiki-instance.shwiki-instance.sh
