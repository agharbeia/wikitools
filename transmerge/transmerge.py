#!/usr/bin/python3

# A tool to help update a localisation file in reference to an updated source file

import json
from collections import OrderedDict

## Definitions:
# catalogue file: Base locale from the newer release. This is the reference for modifications.
# old locale file: Target locale from older release. This is the bse for the new localisation

#1 load catalogue file's content into catalogue memory (CM)
#2 load old localised file's content in the old locale memory (OLM)
#3 for each string in the CM, append each matching string from OLM to the new locale memory (NLM), and remove both strings from the catalogue and locale memories
#4 write the NLM to new.locale
#5 output the strings remaining in CM to the new.base file
#6 output the strings remaining in the OLM to the deleted.locale

##for the sake of simplification of code, English is the base and Arabic is locale, hard-coded, until handling of arguments added.

#read old locale strings from file into memory
print("Reading old locale file into memory")
with open('ar.json', 'r', encoding='utf-8') as old_locale:
	OLM = json.load(old_locale, object_pairs_hook=OrderedDict)

#read catalogue strings from file into memory
print("Reading catalogue file into memory")
with open('en.json') as catalogue:
	CM = json.load(catalogue, object_pairs_hook=OrderedDict)

#create the new locale memory.
NLM = OrderedDict()

#create a memory to save strings in the catalogue that
# are missing from the old locale.
NCM = OrderedDict()

###
#copy the metadata to NLM from OLM.
#if this is uncommented, then so must be the following block.
##NLM['@metadata'] = OLM.pop('@metadata')

#remove metadata record from CM, just to sync it with the OLM
#in order for the later copyng through iteration to work.
#this is needed only if metadata is copied from OLM to NLM
#independently of the rest of the contents of the OLM.
##try:
##	del CM['@metadata']
##except KeyError:
##	print("Catalogue file contains no metadata")
###

print("Copying strings with id's in catalouge, from old locale memory to new locale memory")
for string_id in CM:
	try:
		NLM[string_id] = OLM.pop(string_id)
	#a string is in catalogue but not in old localisation:
	except KeyError:
		#insert it in new localisation in its expected place
		NLM[string_id] = OLM.pop(string_id)
		#and insert it in a separate memory too
		NCM[string_id] = CM[string_id]
		print("A string found in catalogue that's missing from the old locale: ", string_id)
		new_strings++


#write the NLM to disk in a JSON file
print("Writing localisation strings which are carried over to file")
with open("new.ar.json", 'w', encoding='utf-8') as new_locale:
    json.dump(NLM, new_locale, ensure_ascii=False, indent='\t')

#write the NCM to disk in a JSON file
print("Writing new strings from catalogue to file")
with open("new.en.json", 'w', encoding='utf-8') as new_catalogue:
    json.dump(NCM, new_catalogue, ensure_ascii=False, indent='\t')

#write what remains in OLM to disk in a JSON file
print("Writing left-over localisation strings to file")
with open("del.ar.json", 'w', encoding='utf-8') as del_locale:
    json.dump(OLM, del_locale, ensure_ascii=False, indent='\t')

