#!/usr/bin/python3

# A tool to help update a localisation file in reference to an updated source file
import sys
import argparse

import json
from collections import OrderedDict

## Definitions:
# catalogue file: Base locale from the newer release. This is the reference for modifications.
# old locale file: Target locale from older release. This is the bse for the new localisation

ap = argparse.ArgumentParser()

ap.add_argument("-c", "--catalogue",
		action='store',
		dest='catalogue_file',
		default='en.json',
		help="catalogue file")

ap.add_argument("-o", "--old",
		action='store',
		dest='old_locale_file',
		default='ar.json',
		help="old transltions file")

ap.add_argument("-n", "--new",
		action='store',
		dest='new_locale_file',
		default='new.ar.json',
		help="new transltions file")

ap.add_argument("map"
args = ap.parse_args()

def transfer_localisation:
"""
1 load catalogue file's content into catalogue memory
2 load old localised file's content in the old locale memory
3 for each string in the catalogue_memory, append each matching string from old_locale_memory to the new locale memory, and remove both strings from the catalogue and old locale memories
4 write the new_locale_memory to new.locale
5 output the strings remaining in catalogue_memory to the new.base file
6 output the strings remaining in the old_locale_memory to the deleted.locale

"""

##for the sake of simplification of code, English is the base and Arabic is old locale, hard-coded, until handling of arguments is added.

	#read old locale strings from file into memory
	print("Reading old locale file into memory")
	with open(args.old_locale_file, 'r', encoding='utf-8') as old_locale_file:
		old_locale_memory = json.load(old_locale_file, object_pairs_hook=OrderedDict)

	#read catalogue strings from file into memory
	print("Reading catalogue file into memory")
	with open(args.catalogue_file, 'r') as catalogue_file:
		catalogue_memory = json.load(catalogue, object_pairs_hook=OrderedDict)

	#create the new locale memory.
	new_locale_memory = OrderedDict()

	#create a memory to save strings in the catalogue that
	# are missing from the old locale.
	new_catalogue_memory = OrderedDict()

	###
	#copy the metadata to new_locale_memory from old_locale_memory.
	#if this is uncommented, then so must be the following block.
	##new_locale_memory['@metadata'] = old_locale_memory.pop('@metadata')

	#remove metadata record from catalogue_memory, just to sync it with the old_locale_memory
	#in order for the later copying through iteration to work.
	#This is needed only if metadata is copied from old_locale_memory to new_locale_memory
	#independently of the rest of the contents of the old_locale_memory.
	##try:
	##	del catalogue_memory['@metadata']
	##except KeyError:
	##	print("Catalogue file contains no metadata")
	###

	print("Copying strings with id's existing in the catalouge, from old locale memory to new locale memory")
	for string_id in catalogue_memory:
		try:
			new_locale_memory[string_id] = old_locale_memory.pop(string_id)
		except KeyError:
		#a string is in catalogue but not in old localisation:
			#so insert it in new localisation in its expected place
			#in order to use later when merging
			new_locale_memory[string_id] = catalogue_memory[string_id]
			#and insert it in a separate memory too
			new_catalogue_memory[string_id] = catalogue_memory[string_id]
			print("A string found in catalogue that's missing from the old locale: ", string_id)

	#write the new_locale_memory to disk in a JSON file
	print("Writing localisation strings which are carried over to file")
	with open(args.new_locale_file, 'w', encoding='utf-8') as new_locale_file:
		json.dump(new_locale_memory, new_locale_file, ensure_ascii=False, indent='\t')

	#write the new_catalogue_memory to disk in a JSON file
	print("Writing new strings from catalogue to file.")
	with open("./tests/new.en.json", 'w', encoding='utf-8') as new_catalogue:
		json.dump(new_catalogue_memory, new_catalogue, ensure_ascii=False, indent='\t')

	#write what remains in old_locale_memory to disk in a JSON file
	print("Writing left-over localisation strings to file")
	with open("./tests/del.ar.json", 'w', encoding='utf-8') as del_locale:
		json.dump(old_locale_memory, del_locale, ensure_ascii=False, indent='\t')

def merge_localisation:
"""
Merges new_strings_file with base_locale_file
"""
	#read new strings strings from file into memory
	print("Reading new strings' file from " + args.new_strings_file + " into memory.")
	with open(args.new_strings_file, 'r', encoding='utf-8') as new_strings_file:
		new_strings_memory = json.load(new_strings_file, object_pairs_hook=OrderedDict)

	#read base locale strings from file into memory
	print("Reading locale base string from " + args.locale_base_file + " into memory.")
	with open(args.locale_base_file, 'r') as locale_base_file:
		locale_base_memory = json.load(locale_base_file, object_pairs_hook=OrderedDict)

	for string_id in new_strings_memory:
		locale_base_memory[string_id] = new_strings_memory[string_id]

	#write the merged_locale_memory to disk in a JSON file
	print("Writing merged localisation strings which to file: " + args.locale_merged_file)
	with open(args.locale_merged_file, 'w', encoding='utf-8') as locale_merged_file:
		json.dump(locale_base_memory, locale_merged_file, ensure_ascii=False, indent='\t')

