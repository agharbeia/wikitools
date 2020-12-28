#!/usr/bin/python3

import sys, argparse, json
from collections import OrderedDict

ap = argparse.ArgumentParser(
	description="A tool to maintain a base localisation, with regard to an updated catalogue obtained from upstream.\nAll inputs are assumed to be in JSON localisation resources' format.",
	epilog='© 2020 Ahmad Gharbeia & Maysara Abdulhaq.\nLicensed under GPL version 3 license. See https://www.gnu.org/licenses/gpl-3.0.html',
	fromfile_prefix_chars='@'
)
ap.add_argument('--version', action='version', version='%(prog)s 0.7')

help_text = """
Terminology:
* Base file: A JSON structure containing a localisation resource that is
being maintained separately from the one from the upstream.
* Catalogue file: a JSON structure containing a localisation resource from
the upstream, possibly containing changes, additions and omissions
in the strings, as well as changes in the string id's.

The aim is to produce a base localisation resource that is updated such as that:
* strings introduced upstream are inserted.
* strings removed upstream are removed, saved aside for review,
while preserving the order of strings.

The procedure is comprised of two steps, namely: Sieve and Patch.

Step one: Sieve, has three inputs: base, catalogue, and old catalogue,
and results in the following four outputs:
*	An updated base that is comprised of the base, incorporating the
	strings that were newly introduced upstream, as identified by their
	id's, untranslated, in addition to updating the identifiers that
	have been changed.
*	A plus-diff comprise of only the strings that have been newly
	introduced upstream. These need to be translated.
*	A minus-diff comprised of only the strings that were omitted upstream.
	These are preserved for review.
*	A delta-diff comprised of strings from the catalogue that were changed
	between its release, and the older release from which the base
	localisation is derived.
	These need to be reviewed in order to determine whether the changes are
	significant, and as such worthy of updating the corresponding translations.
	For example, if the base before being processed is derived from
	version 1.31 of the upstream catalogue, and the catalogue is from
	version 1.35, then the delta-diff will contain strings whose id's exist
	in both versions but which content have been changed.

Step two: Patch. Each run patches the strings in base with strings from the
input. This is used mainly for: inserting the added strings (from plus-diff)
after they have been translated; and updating changed strings, if they were
re-translated.

It must be noted that in this step no new strings are actually
inserted in the base file. The id's of new strings must have been already
present in the file, with the strings themselves being in the source
language, which is the outcome from step one.
This is intended to guarantee the ordering of the strings, and that no
artefacts are introduced.
"""
ap0 = argparse.ArgumentParser(add_help=False, description='Common, required arguments.')
ap0.add_argument('base', metavar='BASE', default=sys.stdin, type=argparse.FileType('r', encoding='utf-8'),
		help='Filename from which to read base translation resource. It should contain the translations to be preserved across upstream releases. This will not be modified.')
ap0.add_argument('updated', metavar='UPDATED', default=sys.stdout, type=argparse.FileType('w', encoding='utf-8'),
		help='Filename to write updated base to.')


commands = ap.add_subparsers(title='commands', help='To see how each command is used, invoke it with --help')

	
sievecommand = commands.add_parser('sieve', parents=[ap0], description="""
	""",
	help='Sieves a base localisation against a catalogue in order to produce an updated base, a plus-diff, a minus-diff, and a delta-diff.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

sievecommand.add_argument('--catalogue', required=True, dest='catalogue_file', default='en.json', type=argparse.FileType('r', encoding='utf-8'),
		help='The upstream new version of the strings catalogue. This will not be modified.')

sievecommand.add_argument('--old-catalogue', required=True, dest='old_catalogue_file', type=argparse.FileType('r', encoding='utf-8'),
		help='The older upstream version of the strings catalogue. This will not be modified.')

sievecommand.add_argument('--added', required=True, dest='added_strings_file', default='added.en.json', type=argparse.FileType('w', encoding='utf-8'),
		help='Filename to save newly introduced strings to, when in diff mode, or read added translated strings from, when in patch mode.')

sievecommand.add_argument('--changed', required=True, dest='changed_strings_file', default='changed.en.json', type=argparse.FileType('w', encoding='utf-8'),
		help='Filename to save strings changed between revisions of catalogue.')

sievecommand.add_argument('--dropped', required=True, dest='dropped_strings_file', default='dropped.en.json', type=argparse.FileType('w', encoding='utf-8'),
		help='Filename to save strings that were dropped from the newer version of upstream to.')

patchcommand = commands.add_parser('patch', parents=[ap0], description="""
	Merges strings from one localisation resource into another.
	The strings' identifiers from the patch must be already existing in the base,
	otherwise an exception is thrown.
""",
help='Merges strings from a localisation resource into another.')


def sieve(args):
	UNSYNCHED_ERROR = "The {} and the {} seem to be out of sync!\nA string id in the first was not found in the latter.\nThe base localisation file could be in an inconsistent state."
	
	print("Reading catalogue from: ", args.catalogue_file)
	catalogue = json.load(args.catalogue_file, object_pairs_hook=OrderedDict)

	print("Reading base localisation from: ", args.base_file)
	base = json.load(args.base, object_pairs_hook=OrderedDict)

	print("Reading old catalogue from: ", args.old_catalogue_file)
	old_catalogue = json.load(args.old_catalogue_file, object_pairs_hook=OrderedDict)


	updated_base = OrderedDict()
	added_strings = OrderedDict()
	changed_strings =  OrderedDict()

	###
	#copy the metadata to updated_base from base.
	#if this is uncommented, then so must be the following block.
	##updated_base['@metadata'] = base.pop('@metadata')

	#remove metadata record from catalogue, just to sync it with the base
	#in order for the later copying through iteration to work.
	#This is needed only if metadata is copied from base to updated_base
	#independently of the rest of the contents of the base.
	##try:
	##	del catalogue['@metadata']
	##except KeyError:
	##	print("Catalogue file contains no metadata")
	###

	print("Starting sieving strings; added, dropped and changed.")
	for string_id in catalogue :
		if (string_id in base):	#Is this id carried over?
			#Yes. Copy its translated string:
			updated_base[string_id] = base.pop(string_id)		
			
			try:
				#Has the string has been changed between upstream releases?
				if not (catalogue[string_id] == old_catalogue[string_id]):
					#Yes. So also save its source string for review.
					changed_strings[string_id] = catalogue[string_id]
			except KeyError:
				print(UNSYNCHED_ERROR.format('base', 'old catalogue'))
				
		else:	#No. It seems to be a new string.
			#Check for a change in id with unchanged string
			#by comparing with strings from the older catalogue.
			for old_id in old_catalogue :
				if (old_catalogue[old_id] == catalogue[string_id]):
					print(f"A string is found with different id: '{old_id}' ⇒ '{string_id}'.")
					#This string is found in the old catalogue.
					Print("It either has its id changed, or it's new but repeated.")
					#Anyhow, save its translation with the new id in the updated base.
					try:
						updated_base[string_id] = base.pop[old_id]
					except KeyError:
						print(UNSYNCHED_ERROR.format('old catalogue', 'base'))
				else:
					print("Found newly introduced string: ", string_id)
					#..so insert it, untranslated, in updated base at its
					updated_base[string_id] = catalogue[string_id]

					#..and insert it in a separate dictionary of added strings too
					#in order for translators to work on it.
					added_strings[string_id] = catalogue[string_id]
	
	print("Sieving strings completed.")		
	#..now what remains in base dictionary are dropped strings.			
	
	print(f"Writing {updated_base.len()} carried-over strings to updated base file {args.updated}")
	json.dump(updated_base, args.updated_base_file, ensure_ascii=False, indent='\t')

	print(f"Writing {added_strings.len()} newly added strings to file {args.added_strings_file}")
	json.dump(added_strings, args.added_strings_file, ensure_ascii=False, indent='\t')

	print(f"Writing {base.len()} dropped strings to file {args.dropped_strings_file}")
	json.dump(base, args.dropped_strings_file, ensure_ascii=False, indent='\t')
	
	print(f"Writing {changed_strings.len()} changed catalogue strings file {args.changed_strings_file}")
	json.dump(changed_strings, args.changed_strings_file, ensure_ascii=False, indent='\t')


def patch(args):
	print('Reading base localisation from: ', args.base)
	base = json.load(args.base_file, object_pairs_hook=OrderedDict)

	print('Reading patch from: ', args.patch_file)
	patch = json.load(args.patch_file, object_pairs_hook=OrderedDict)

	try:
		for string_id in patch :
			base[string_id] = patch[string_id]
	except KeyError:
		raise SystemExit('The patch contains a string with an id which does not exist in base. Aborting.')
	else:
		print('Writing patched localisation file to: ', args.updated)
		json.dump(base, args.updated, ensure_ascii=False, indent='\t')

try:
	sievecommand.set_defaults(func=sieve)
	patchcommand.set_defaults(func=patch)

	args = ap.parse_args()

	args.func(args)
except AttributeError:
	ap.print_usage()
