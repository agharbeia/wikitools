#!/usr/bin/python3

"""
Terminology:
	* Base translation: The localisation resource that is being maintained
	  separately from upstream.
	* Upstream localisation catalogue: the version of the localisation
	  against which the base should be synchronised. It should be of the same
	  version as the source catalogue. This is an optional input that enhances
	  the quality of the output by removing untranslatable strings from outputs.
	* Source catalogue: The localisation resource from the upstream in the
	  source language, possibly containing changes, additions and omissions
	  in the strings, as well as changes in the string id's.
	* Old source catalogue: the version of the catalogue from which the base
	  translation is derived.
	Each of the above is expected to be a JSON object of key value pairs,
	One element in which could be named "@metadata", that is preserved as is.

The aim is to produce a base localisation resource that is updated such as that:
	* strings introduced upstream are inserted.
	* strings removed upstream are removed, saved aside for review,
	  while preserving the order of strings.

The procedure is comprised of two steps, namely: Sieve and Patch.

Step one: Sieve, has three inputs: base, catalogue, and old catalogue,
and results in the following four outputs:
	* An updated base that is comprised of the base, incorporating the
	  strings that were newly introduced upstream, as identified by their
	  id's, untranslated, in addition to updating the identifiers that
	  have been changed.
	* A plus-diff comprise of only the strings that have been newly
	  introduced upstream. These need to be translated.
	* A minus-diff comprised of only the strings that were omitted upstream.
	  These are preserved for review.
	* A delta-diff comprised of strings from the catalogue that were changed
	  between its release, and the older release from which the base
	  localisation is derived.
	  These need to be reviewed in order to determine whether the changes are
	  significant, and as such worthy of updating the corresponding translations.
	  For example, if the base before being processed is derived from
	  version 1.31 of the upstream catalogue, and the catalogue is from
	  version 1.35, then the delta-diff will contain strings whose id's exist
	  in both versions but which content have been changed.
	* If a an upstream localisation has been provided, then it will be used to
	  filter all outputs except dropped strings, thus ensuring that only strings
	  that are currently used are eventually included in the updated base.
	  However, if the version of the upstream does not match that of the
	  catalogue, then discrepancy can result.

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

import sys, argparse, json
from collections import OrderedDict

ap = argparse.ArgumentParser(
	description="""A tool to maintain a base localisation, with regard to an updated catalogue obtained from upstream.
	All inputs are assumed to be in JSON localisation resources' format.""",
	epilog='© 2020 Ahmad Gharbeia & Maysara Abdulhaq.\nLicensed under GPL version 3 license. See https://www.gnu.org/licenses/gpl-3.0.html',
	fromfile_prefix_chars='@'
)
ap.add_argument('--version', action='version', version='%(prog)s 0.7')

ap.add_argument('--long-story', action='store_true', help='Print verbose description of the programme.')

ap0 = argparse.ArgumentParser(add_help=False, description='Common, required arguments.')

ap0.add_argument('--quiet', action='store_true', help='Do not print progress messages.')

ap0.add_argument('base', metavar='BASE', default=sys.stdin, type=argparse.FileType('r', encoding='utf-8'),
		help='Filename from which to read base translation resource. It should contain the translations to be preserved across upstream releases. This will not be modified.')

ap0.add_argument('updated', metavar='UPDATED', default=sys.stdout, type=argparse.FileType('w', encoding='utf-8'),
		help='Filename to write updated base to.')


commands = ap.add_subparsers(title='commands', help='To see how each command is used, invoke it with --help')


sievecommand = commands.add_parser('sieve', parents=[ap0], description="""
	""",
	help='Sieves a base localisation against a catalogue in order to produce an updated base, a plus-diff, a minus-diff, and a delta-diff.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

sievecommand.add_argument('--upstream', default=argparse.SUPPRESS, type=argparse.FileType('r', encoding='utf-8'),
		help='The upstream version of the localised strings catalogue, against which the base should be synchronised. This will not be modified.')

sievecommand.add_argument('--catalogue', required=True, default='en.json', type=argparse.FileType('r', encoding='utf-8'),
		help='The upstream new version of the source strings catalogue. This will not be modified.')

sievecommand.add_argument('--old-catalogue', required=True, type=argparse.FileType('r', encoding='utf-8'),
		help='The older upstream version of the source strings catalogue. This will not be modified.')

sievecommand.add_argument('--added', nargs='?', dest='added_strings', default='added.json', type=argparse.FileType('w', encoding='utf-8'),
		help='Filename to save newly introduced strings to, when in diff mode, or read added translated strings from, when in patch mode.')

sievecommand.add_argument('--changed', nargs='?', dest='changed_strings', default='changed.json', type=argparse.FileType('w', encoding='utf-8'),
		help='Filename to save strings changed between revisions of catalogue.')

sievecommand.add_argument('--dropped', nargs='?', dest='dropped_strings', default='dropped.json', type=argparse.FileType('w', encoding='utf-8'),
		help='Filename to save strings that were dropped from the newer version of upstream to.')

patchcommand = commands.add_parser('patch', parents=[ap0], description="""
	Merges strings from one localisation resource into another.
	The strings' identifiers from the patch must be already existing in the base,
	otherwise an exception is thrown.
""",
	help='Merges strings from a localisation resource into another.')

patchcommand.add_argument('--patch', required=True, dest='patch', type=argparse.FileType('r', encoding='utf-8'),
		help='Localisation string, modified somehow, to patch the base with. This will not be modified.')
	

def sieve(args):

	def report(*s):
		if not args.quiet:
			print(*s, file=sys.stderr)
	
	report('Reading catalogue from: ', args.catalogue.name)
	catalogue = json.load(args.catalogue, object_pairs_hook=OrderedDict)
	report(len(catalogue), 'strings read.')

	report('Reading base localisation from: ', args.base.name)
	base = json.load(args.base, object_pairs_hook=OrderedDict)
	report(len(base), 'strings read.')

	report('Reading old catalogue from: ', args.old_catalogue.name)
	old_catalogue = json.load(args.old_catalogue)
	report(len(old_catalogue), 'strings read.')

	report("Reading of inputs completed.")
	
	#Create structures for outputs
	updated = OrderedDict()
	added_strings = OrderedDict()
	changed_strings =  OrderedDict()

	#Copy the metadata to updated base from base.
	try:
		report('Copying metadata from base.')
		updated['@metadata'] = base.pop('@metadata')
	except KeyError:
		report('Base contains no metadata!')

	#Remove metadata records from catalogue, order to sync it with the base
	#in order for the later copying through iteration to work.
	try:
		del catalogue['@metadata']
	except KeyError:
		report('Catalogue contains no metadata!')

	report('\nStarting sieving strings; added, dropped and changed.')

	for string_id in catalogue :
		newStringFound = False

		if (string_id in base):	#Is this id carried over?
			#Yes. Migrate its translated string from base:
			updated[string_id] = base.pop(string_id)

			#Has the source string been changed between upstream source releases?
			if ((string_id in old_catalogue) and (not catalogue[string_id] == old_catalogue[string_id])):
				#Yes. So also save its source string for review.
				print(f"String with id: '{string_id}' was changed in source.", file=sys.stderr)
				changed_strings[string_id] = catalogue[string_id]
			#else: It either hasn't changed, or it didn't exist in the version of
			#old catalogue we're looking at, which means the base translation
			#is out of synch with the old catalogue. Either way, we do not care.
		else:	#No. It seems to be a new string (as far as the base is concerned).
			#Must now check whether the string existed in the old catalogue
			#with a different id.
			if (not string_id in old_catalogue):
				for old_id in old_catalogue :
					if ((catalogue[string_id] == old_catalogue[old_id]) and (not old_id in catalogue)) :
						#This string is found in the old catalogue but with a different id.
						print(f"A string is found with different id: '{old_id}' ⇒ '{string_id}'.", file=sys.stderr)
						if (old_id in base):
							#Save its existing translation to the updated base, with the new id.
							updated[string_id] = base.pop(old_id)
						else:
							newStringFound = True;
							#We now know that base is not in sync with old catalogue.
							#But we do not care.
						break #Stop the search,.either way.
			else:
				newStringFound = True;

		if newStringFound :
			#Id existed in old catalogue but not in base, so it is new:
			report('Found newly introduced string: ', string_id)
			#..so insert it, untranslated, in updated base at its order
			updated[string_id] = catalogue[string_id]

			#..and insert it in a separate dictionary of added strings too
			#in order for translators to work on it.
			added_strings[string_id] = catalogue[string_id]

	if hasattr(args, 'upstream'):
		#If an upstream localisation has been provided,
		#filter the updated base as well as added and changed strings against it.
		#The advantage of this is excluding untranslatable strings, but
		#could have the drawback of omitting some strings, if the versions
		#of the upstream translation is not fully in sync with the catalogue.
		report('\nAn upstream localisation was specified. It will be used as filter.')
		report('Reading upstream localisation from: ', args.upstream.name)
		upstream = json.load(args.upstream)
		report(len(upstream), 'strings read.')
		for strings in [updated, added_strings, changed_strings]:
			for string_id in list(strings):
				if (not string_id in upstream):
						report('Omitting string with id', string_id)
						del strings[string_id]

	report('\nSieving strings completed.')
	#..now what remains in base dictionary are dropped strings.

	report(f"Writing {len(updated)} carried-over and added strings to {args.updated.name}")
	json.dump(updated, args.updated, ensure_ascii=False, indent='\t')

	report(f"Writing {len(added_strings)} newly added strings to {args.added_strings.name}")
	json.dump(added_strings, args.added_strings, ensure_ascii=False, indent='\t')

	report(f"Writing {len(changed_strings)} changed catalogue strings to {args.changed_strings.name}")
	json.dump(changed_strings, args.changed_strings, ensure_ascii=False, indent='\t')

	report(f"Writing {len(base)} dropped (or refactored) strings to {args.dropped_strings.name}")
	json.dump(base, args.dropped_strings, ensure_ascii=False, indent='\t')


def patch(args):
	report('Reading base localisation from: ', args.base)
	base = json.load(args.base, object_pairs_hook=OrderedDict)

	report('Reading patch from: ', args.patch)
	patch = json.load(args.patch)

	try:
		for string_id in patch :
			base[string_id] = patch[string_id]
	except KeyError:
		raise SystemExit('The patch contains a string with an id which does not exist in base. Aborting.')
	else:
		report('Writing patched localisation to: ', args.updated)
		json.dump(base, args.updated, ensure_ascii=False, indent='\t')

try:
	sievecommand.set_defaults(func=sieve)
	patchcommand.set_defaults(func=patch)
	args = ap.parse_args()
#print(args)
	if args.long_story:
		print(sys.modules[__name__].__doc__)
	else:
		args.func(args)
except AttributeError:
	ap.print_usage()
