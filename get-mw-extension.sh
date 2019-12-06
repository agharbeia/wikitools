#!/bin/sh
## usage:
## > get-mw-extension.sh extensionID
## for example:
## >  get-mw-extension.sh InviteSignup-REL1_28-6643368
## will download $EXT_DIST/InviteSignup-REL1_28-6643368.tar.gz, extract its contents into $MW_BASE/$EXT_DIR/InviteSignup-REL1_28-6643368
## and link to it from $MW_BASE/$MW_EXT_DIR/InviteSignup, assuming their relative relation is ../../
EXT_DIST=https://extdist.wmflabs.org/dist/extensions/
MW_BASE=/var/www/wiki
EXT_DIR=mw-extensions
MW_EXT_DIR=mediawiki/extensions

mkdir "$MW_BASE/$EXT_DIR/$1"
wget --output-document=- $EXT_DIST/$1.tar.gz | tar --file - --extract --ungzip --owner=www-data --group=adm --directory "$MW_BASE/$EXT_DIR/$1" --strip-components=1
ln --symbolic "../../$EXT_DIR/$1" "$MW_BASE/$MW_EXT_DIR/${1%%-*}"
