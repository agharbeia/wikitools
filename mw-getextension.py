#!/usr/bin/python3

from urllib.request import urlopen
import argparse, re, os

help_text = """
Downloads Mediawiki extensions through the Extension Distributor.
"""

Distributor_URL = 'https://www.mediawiki.org/wiki/Special:ExtensionDistributor'
MW_VER = '1.35'

def main(args):
	print('Downloading MW extensions for versoin ' + args.mw_version)

	ver_id = args.mw_version.replace('.','_')
	
	for extension in args.extension:
		print("Processing requested extension {}".format(extension))

		if args.verbose: print('\tFetching page at: ' + Distributor_URL + '?extdistname=' + extension + '&extdistversion=REL' + args.mw_version.replace('.','_'))
		html = urlopen(Distributor_URL + '?extdistname=' + extension + '&extdistversion=REL' + ver_id).read().decode()

		regex = 'https:\/\/extdist\.wmflabs\.org\/dist\/extensions\/(?P<bundle>' + extension + '-REL' + ver_id + '-\w{7})\.tar\.gz'
		if args.verbose: print('\tSearching for RegEx pattern: ' + regex)
		match = re.search(regex, html)
		bundle_URL = match.group()
		
		print('\tDownloading from ' + bundle_URL)
		print('\t' + ('…and extracting the bundle' if not args.no_extract else '') + ' to ' + args.target_dir)
		os.system('wget --continue' + (' --output-document - ' if not args.no_extract else ' --directory-prefix={} '.format(args.target_dir)) + bundle_URL + ('' if args.no_extract else ' | tar --directory={} --extract --file=- --gunzip'.format(args.target_dir)) + ' && mv {0}/{1} {0}/{2}'.format(args.target_dir, extension, match.group('bundle')))
## end main

ap = argparse.ArgumentParser(description=help_text, epilog='By Ahmad Gharbeia, November 2020; Under GPL 3.0 license')

ap.add_argument('extension', nargs='+',
		help='Name of the MW extension.')

ap.add_argument('--mw-version', action='store', default=MW_VER,
	help='The major release version of Mediawiki to get extensions for. It currently defults to ' + MW_VER)

ap.add_argument('--target-dir', action='store', default='./',
	help='The name of the directory to save bundle or extract it to.')
                    
ap.add_argument('--no-extract', action='store_true', default=False,
  help='Download the extension bundle but do not extract it.')

ap.add_argument('--verbose', action='store_true', default=False,
	help='Output more details about what\'s happening.')

main(ap.parse_args())
