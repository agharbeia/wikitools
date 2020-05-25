#!/usr/bin/python3

import sys
import argparse
import json
from collections import OrderedDict

help_text = """
A tool to maintain a forked localisation, with regard to an updated catalogue.

It is used to merge a localisation that is different from that released by
the upstream localisers into the corresponding newer upstream localisation
while keeping the differences from the fork, and accounting for the addition
and deletion of strings.

The procedure is two-step: first a localisation file is produced that has the
forked localisation and any strings added in the newer release from upstream,
untranslated.
In a later step, after the added strings have been translated, they are
merged back in the final localisation file.

In the first step, strings from the forked localisation that still exist in
the new version of the upstream are copied to the output, while strings
that are dropped upstream are omitted from the output, but are kept in
a separate file for reference (sometimes only a string's identifier is changed,
but can still be reused after re-identification). Additionally, strings that
are newly introduced upstream are also copied in the output of the first stage,
and simultaneously written to a separate file. This makes it easier to locate
them and translate them.

In the second step, strings that are introduced upstream, after being
translated, are inserted back in the output from step one, over-writing their
non-translated counterparts, thus producing the final result.
"""

ap = argparse.ArgumentParser()

ap.add_argument("-c", "--catalogue", action='store', dest='catalogue_file', default='en.json',
		help="The upstream new version of the strings catalogue.")

ap.add_argument("-f", "--forked", action='store', dest='forked_locale_file', default='ar.json',
		help="Forked translation file, containing the translations to be preserved across upstream releases.")

ap.add_argument("-a", "--added", action='store', dest='added_strings_file', default='added.en.json',
		help="File to write added untranslated strings to, or read added translated strings from.")

ap.add_argument("-d", "--dropped", action='store', dest='dropped_strings_file', default='dropped.en.json',
		help="File to write dropped strings to.")

ap.add_argument("-o", "--ouput", action='store', dest='output_file', default='output.ar.json',
		help="Output file, content depends on the requested operation.")

args = ap.parse_args()

def transfer_localisation():
	"""
	1 load catalogue strings
	2 load strings from the forked localisation
	3 for each string in the catalogue, copy the matching string from the fork to the output, and remove the string from the catalogue.
	4 write the output localisation memory to a file (carried over).
	5 write the strings that remain in the catalogue memory to a file (new).
	6 write the strings that remain in the forked localisation memory to a file (deleted).
	"""

	print("Reading catalogue from: ", args.catalogue_file)
	with open(args.catalogue_file, 'r') as catalogue_file:
		catalogue_memory = json.load(catalogue, object_pairs_hook=OrderedDict)

	print("Reading forked localisation from: ", args.forked_locale_file)
	with open(args.forked_locale_file, 'r', encoding='utf-8') as forked_locale_file:
		forked_locale_memory = json.load(forked_locale_file, object_pairs_hook=OrderedDict)


	#create the new locale memory.
	output_memory = OrderedDict()

	#create a memory to save strings in the catalogue that
	# are missing from the old locale.
	new_catalogue_memory = OrderedDict()

	###
	#copy the metadata to output_memory from forked_locale_memory.
	#if this is uncommented, then so must be the following block.
	##output_memory['@metadata'] = forked_locale_memory.pop('@metadata')

	#remove metadata record from catalogue_memory, just to sync it with the forked_locale_memory
	#in order for the later copying through iteration to work.
	#This is needed only if metadata is copied from forked_locale_memory to output_memory
	#independently of the rest of the contents of the forked_locale_memory.
	##try:
	##	del catalogue_memory['@metadata']
	##except KeyError:
	##	print("Catalogue file contains no metadata")
	###

	print("Copying strings with id's existing in the catalouge, from old locale memory to new locale memory")
	for string_id in catalogue_memory:
		try:
			output_memory[string_id] = forked_locale_memory.pop(string_id)
		except KeyError:
			print("Found newly introduced string: ", string_id)
			#..so insert it, untranslated, in ouput file at its
			#expected location in order to use it later when merging.
			output_memory[string_id] = catalogue_memory[string_id]

			#and insert it in a separate memory of added strings too
			#in order for translators to work on it.
			added_strings_memory[string_id] = catalogue_memory[string_id]

	print("Writing strings which are carried over to file: ", args.output_file)
	with open(args.output_file, 'w', encoding='utf-8') as output_file:
		json.dump(output_memory, output_file, ensure_ascii=False, indent='\t')

	print("Writing newly introduced strings to file: ", args.added_strings_file)
	with open(args.added_strings_file, 'w', encoding='utf-8') as added_strings_file:
		json.dump(added_strings_memory, new_catalogue, ensure_ascii=False, indent='\t')

	print("Writing dropped strings to file: ", args.dropped_strings_file)
	with open(args.dropped_strings_file, 'w', encoding='utf-8') as dropped_strings_file:
		json.dump(forked_locale_memory, dropped_strings_file, ensure_ascii=False, indent='\t')

def merge_localisation():
	"""
	Merges added strings into forked localisation.

	"""
	print("Reading forked localisation from: ", args.forked_locale_file)
	with open(args.forked_locale_file, 'r', encoding='utf-8') as forked_locale_file:
		forked_locale_memory = json.load(forked_locale_file, object_pairs_hook=OrderedDict)

	print("Reading added strings from: ", args.added_strings_file)
	with open(args.added_strings_file, 'r', encoding='utf-8') as added_strings_file:
		added_strings_memory = json.load(added_strings_file, object_pairs_hook=OrderedDict)

	for string_id in added_strings_memory:
		forked_locale_memory[string_id] = added_strings_memory[string_id]

	print("Writing merged localisation strings to file: ", args.output_file)
	with open(args.output_file, 'w', encoding='utf-8') as output_file:
		json.dump(forked_locale_memory, output_file, ensure_ascii=False, indent='\t')

