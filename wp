#!/usr/bin/python
# if you're using an old version of python you might also want the patched zipfile that can extract folders
# get the zipfile.py from here: http://pastebin.com/9wGMFKiL
import urllib2
import tarfile, zipfile
import os
import re

import getopt, sys

def main():
	optlist, args = getopt.getopt(sys.argv[1:], [], [])
	action = args[0]
	
	if action == 'get':
		what = args[1]
		if what == 'theme':
			# download a theme
			pass
		elif what == 'plugin':
			# download a plugin
			plugin_name = args[2]
			try:
				plugin_version = args[3]
			except IndexError, e:
				plugin_version = 'latest'
				
			get_plugin(plugin_name=plugin_name, plugin_version=plugin_version)
		else:
			# download WordPress
			get_wordpress(core_version=what)
		
	exit();
	
def get_wordpress(core_version):
	
	if core_version == 'latest':
		filename = 'latest.tar.gz'
	else:
		filename = 'wordpress-%s.tar.gz' % core_version
	
	url = 'http://wordpress.org/%s' % filename	
	response = urllib2.urlopen(url)
	f = open(filename, 'w')
	
	print 'Downloading: %s' % filename
	
	while True:
		buffer = response.read(8192)
		if not buffer:
			break

		f.write(buffer)
		
	f.close()
	
	print 'Extracting: %s' % filename
	
	tar = tarfile.open(filename)
	tar.extractall()
	tar.close()
	
	print 'Cleaning up'
	os.remove(filename)
	
	print 'Done'
	
def get_plugin(plugin_name, plugin_version):
	plugins_dir = locate_wordpress('/wp-content/plugins/')
	
	print 'Fetching plugin information'
	readme_file_url = 'http://plugins.svn.wordpress.org/%s/trunk/readme.txt' % plugin_name
	response = urllib2.urlopen(readme_file_url)
	readme_file = response.read()
	readme_file = readme_file.replace('\r\n', '\n')
	
	m = re.search('^Stable tag: (.+)?$', readme_file, re.MULTILINE)
	stable_tag = m.group(1)
	
	m = re.search('^=== (.+) ===$', readme_file, re.MULTILINE)
	plugin_title = m.group(1)
	filename = '%s.%s.zip' % (plugin_name, stable_tag)
	
	print 'Found: %s v %s' % (plugin_title, stable_tag)
	
	download_url = 'http://downloads.wordpress.org/plugin/%s' % filename
	print 'Downloading: %s' % filename

	response = urllib2.urlopen(download_url)
	f = open(plugins_dir + filename, 'w')
	
	while True:
		buffer = response.read(8192)
		if not buffer:
			break

		f.write(buffer)
		
	f.close()
	
	print 'Extracting: %s' % filename
	archive = zipfile.ZipFile(plugins_dir + filename)
	archive.extractall(plugins_dir)
	archive.close()
	
	print 'Cleaning up'
	os.remove(plugins_dir + filename)
	
	print 'Done'

def locate_wordpress(append_path):
	current_dir = os.getcwd().split('/')
	while True:
		config_file = '/'.join(current_dir) + '/wp-config.php'
		# print 'Trying %s' % config_file
		if os.path.exists(config_file):
			break
			
		current_dir = current_dir[:-1]
		if len(current_dir) < 1:
			print('Fatal: Could not locate WordPress')
			exit()
			
	return '/'.join(current_dir) + append_path

if __name__ == '__main__':
	main()