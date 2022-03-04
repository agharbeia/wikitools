#!/bin/bash

#   Configuration variables used in this script,
#+ and in the configuration files' templates.
#
MW_VER=${5-'1.35.5'}

# Wiki configuration:
APEX=wikido.xyz
MW_INSTANCE_DIR=mw
URL_PREFIX=""   #with leading slash
REPO_ALIAS=repo

# Directories:
MW_SOURCE=/srv/app/mediawiki/$MW_VER/core
TEMPLATES_SOURCE=/srv/src/wikitools/templates
SECRETS_DIR=/srv/websecrets
REPO_BASE_DIR=/srv/repositorea

# Templates:
DB_TEMPLATE=$TEMPLATES_SOURCE/wikido.xyz.mw-$MW_VER.sql


###=========
if [[ -z $1 || -z $2 || -z $3 || -z $4 ]]; then
	cat <<- USAGE >&2
		WikiFamily configuration generator, and database creator.
		usage:
		  $(basename $0) <handle> <title> <username> <password> <mw_ver>
		where:
		    <handle>: A string to be used as the the hostname for the wiki website, as well as the base of both the database name and database username.
		    <title>: The natural language title of the wikisite.
		    <username>: Username of the first user to be created; and granted both "sysop" and "bureaucrat" status.
		    <password>: Password for aforementioned user.
		    <mw_version>: an optoinal MW version number to construct paths. Currently defaults to $MW_VER
		More configuration variables exist in the code to customise the process.
		This scritp needs to be run as root. All arguments are required.
USAGE
	exit 85
fi
if ! [ $(id -u) = 0 ]; then
   echo "The script needs to be run as root." >&2
   exit 1
else
    real_user=$SUDO_USER
fi

WIKI_HANDLE=$1
WIKI_TITLE=$2
WIKI_USER=$3
WIKI_PASS=$4

echo -e "Creating instance for:\nHandle: $WIKI_HANDLE\nTitle: $WIKI_TITLE\nMW version: $MW_VER" >&2

#
# Derivative constants:
FAMILY_ROOT=/srv/www/$APEX
WIKI_ROOT=$FAMILY_ROOT/$WIKI_HANDLE
WIKI_FQDN=$WIKI_HANDLE.$APEX
REPOSITORY_DIR=$REPO_BASE_DIR/$APEX/$WIKI_HANDLE
CACHE_DIR=/var/cache/$APEX/$WIKI_HANDLE
TEMP_DIR=/var/tmp/$APEX/$WIKI_HANDLE
DB_NAME=${WIKI_HANDLE}_wiki
DB_USER=wiki_${WIKI_HANDLE}

# Create directories and most needed symbolic links, acting as the apache user
sudo -u www-data mkdir --parents $WIKI_ROOT
sudo -u www-data ln --symbolic $MW_SOURCE $WIKI_ROOT/$MW_INSTANCE_DIR
sudo -u www-data cp --recursive $MW_SOURCE/images $REPOSITORY_DIR
sudo -u www-data cp --recursive $MW_SOURCE/cache $CACHE_DIR
sudo -u www-data mkdir --parents $TEMP_DIR
mkdir --parents $SECRETS_DIR && chgrp www-data $SECRETS_DIR

conf_from_template() {
# Magically generates configuration files based on templates.
  TEMPLATE=$1
  shift
  eval "`printf 'local %s\n' $@`
  cat <<EOF
`sudo -u www-data cat $TEMPLATE`
EOF"
}


# Generate LocalSettings.php for the wiki.
# This instance-specific file is invoked from a dispatcher at the wikifamily-level
conf_from_template "$TEMPLATES_SOURCE/LocalSettings.template" > "$WIKI_ROOT/LocalSettings.php"

#Generate Apache configuration
conf_from_template "$TEMPLATES_SOURCE/apache.$APEX.conf.template" > "/etc/apache2/sites-available/$WIKI_FQDN.conf"

sudo -u www-data cp "$TEMPLATES_SOURCE/robots.txt.template" "$WIKI_ROOT/robots.txt"

#Generate websecrets files
DB_PASSWORD=$(apg -a1 -n1 -m16 -MNCL -d) #This is entropy expensive, so better not run it unless it's feasible

conf_from_template "$TEMPLATES_SOURCE/websecrets.template" > "$SECRETS_DIR/$WIKI_HANDLE.$APEX"
chmod u=r,g=r,o=- "$SECRETS_DIR/$WIKI_HANDLE.$APEX"

#Create database
echo "CREATE USER '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD'; CREATE DATABASE $DB_NAME; GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';" | mysql --user=root --password && echo -e "Successfuly created database $DB_NAME; user $DB_USER, and granted permissions.\nDatabase user's password is $DB_PASSWORD." >&2

mysql --user=$DB_USER --password=$DB_PASSWORD $DB_NAME < $DB_TEMPLATE && echo "Successfuly created Mediawiki tables in $DB_NAME." >&2


#create 1st wiki user
sudo -u www-data php "$MW_SOURCE/maintenance/createAndPromote.php" --bureaucrat --sysop --wiki "$DB_NAME" "$WIKI_USER" $WIKI_PASS

#create logo
#HANDLE_HASH=$(jacksum -a $CHECKSUM -F "#CHECKSUM" -X -q txt:$WIKI_HANDLE)
HANDLE_HASH=$(echo -n $WIKI_HANDLE | md5sum)

COLOUR1=${HANDLE_HASH:0:6}
COLOUR2=$(for o in {0..4..2}; do printf '%02X' $(( (0x${HANDLE_HASH:o:2} + 0x80) % 0xFF )); done)

if [[ 0x$COLOUR1 -lt 0x$COLOUR2 ]]; then
	FILL1=#$COLOUR2
	FILL2=#$COLOUR1
else
	FILL1=#$COLOUR1
	FILL2=#$COLOUR2
fi
conf_from_template $TEMPLATES_SOURCE/wikido.xyz-logo.svg.template > $WIKI_ROOT/logo.svg
sudo -u www-data php $MW_SOURCE/maintenance/importImages.php --wiki $DB_NAME --extensions=svg --skip-dupes --comment='شعار ويكي $WIKI_FQDN بألوان مستنبطة من عنوانها' --license='برخصة_المشاع_الإبداعي_النسبة_4.0' $WIKI_ROOT


a2ensite $WIKI_FQDN.conf

#restart apache if configuration is OK
apache2ctl configtest && apache2ctl restart
