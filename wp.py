#!/usr/bin/python
# if you're using an old version of python you might also want the patched zipfile that can extract folders
# get the zipfile.py from here: http://pastebin.com/9wGMFKiL

"""
WordPress CLI (Command Line Interface)
Author: Konstantin Kovshenin
Contributors: Pedro Sola
License: GPLv2
Version: <none>

URL: https://github.com/kovshenin/wordpress-cli
"""

import urllib2
import tarfile, zipfile
import os, re

import getopt, sys

class WordPressCLI(object):
	"""
	The WordPress CLI class, handles all the command line interface
	logic through actions_available, each of which represents a
	method inside this class.
	"""
	
	options_available = {'short': [], 'long': ['debug', 'dir-name=']}
	actions_available = ['get', 'update', 'create', 'backup']
	
	def __init__(self):
		"""
		Parses the options from sys.argv and divides them into options
		and arguments, where options begin with - or -- while arguments
		are simple commands.
		"""
		
		# Bring the -- and - options in front of the string so that
		# getopt() could recognize them as options, since order doesn't matter.
		options = []
		args = []
		for arg in sys.argv[1:]:
			if arg.startswith('-') or arg.startswith('--'):
				options.append(arg)
			else:
				args.append(arg)
				
		argv = options + args
		
		self.options, self.args = getopt.getopt(argv, self.options_available['short'], self.options_available['long'])
		
		# Convert options to a dict
		options = {}
		for option_key, option_value in self.options:
			options[option_key] = option_value
		self.options = options
		
		self.debug = '--debug' in self.options
		self.action = None
		
		if self.debug:
			print
			print 'WordPress CLI Running in Debug Mode'
		
		if len(self.args) > 0:
			self.action = self.args[0]
		
	def execute(self):
		if self.action in self.actions_available:
			if hasattr(self, self.action):
				f = getattr(self, self.action)
				f()
			else:
				raise Exception('Not implemented yet.')
		else:
			raise Exception('Action not available: %s' % self.action)
			
	def get(self):
		"""
		Download and unpack something from WordPress.org, works with
		the wordpress core, themes and plugins.
		"""
		
		if len(self.args) > 1: # wp <first-arg> <second-arg>
			object_to_get = self.args[1]
			if object_to_get == 'theme':
				return self.get_theme() # wp get theme <theme-slug>
			elif object_to_get == 'plugin':
				return self.get_plugin() # wp get plugin <plugin-slug>
			elif object_to_get == 'core':
				return self.get_core() # wp get core <version-slug>
		else:
			# @todo Help messages
			print "The get command will download and unpack something from WordPress"
		
	def get_theme(self):
		"""
		Download a theme from the WordPress repository, the command line arguments are:
		# wp get theme <theme-slug> [<version>]
		"""
		
		if len(self.args) > 2:
			theme_slug = self.args[2]
			
		else:
			raise Exception('You must supply a theme slug.')
		
	def _get_theme(self, theme_slug, version='latest'):
		"""
		Wrapped by self.get_theme in the CLI although used by other commands as well,
		for ex. when creating a child theme and parent theme does not exist.
		"""
		pass
		
	def get_plugin(self):
		"""
		Download and unpack a plugin from the WordPress.org repository, arguments are:
		# wp get plugin <plugin-name> [<version>]
		"""
		
		if len(self.args) > 2:
			plugin_name = self.args[2]
			plugin_version = self.args[3] if len(self.args) > 3 else 'latest'
			plugins_dir = self.config_dir() + '/wp-content/plugins/'

			print 'Fetching plugin information'
			readme_file_url = 'http://plugins.svn.wordpress.org/%s/trunk/readme.txt' % plugin_name
			response = urllib2.urlopen(readme_file_url)
			readme_file = response.read()
			readme_file = readme_file.replace('\r\n', '\n')

			m = re.search('^Stable tag: (.+)?$', readme_file, re.MULTILINE)
			stable_tag = m.group(1)

			m = re.search('^=== (.+) ===$', readme_file, re.MULTILINE)
			plugin_title = m.group(1)
			
			if plugin_version == 'latest':
				filename = '%s.%s.zip' % (plugin_name, stable_tag)
				print 'Latest version: %s v %s' % (plugin_title, stable_tag)
			else:
				filename = '%s.%s.zip' % (plugin_name, plugin_version)

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
			
			# Let's see if a previous version exists, and if it does, run
			# a recursive delete on the whole path.
			if os.path.exists(plugins_dir + plugin_name):
				print 'Removing previous version'
				rm_rf(plugins_dir + plugin_name)

			print 'Extracting: %s' % filename
			archive = zipfile.ZipFile(plugins_dir + filename)
			archive.extractall(plugins_dir)
			archive.close()
			
			# Clean up -- remove the archive
			os.remove(plugins_dir + filename)
			
		else:
			raise Exception('You must specify a plugin name.')
		
	def get_core(self):
		
		# Let's see if the user has asked for a specific version, capitalize RC
		version = self.args[2] if len(self.args) > 2 else 'latest'
		version = version.replace('rc', 'RC')
		filename = 'latest.tar.gz' if version == 'latest' else 'wordpress-%s.tar.gz' % version

		# Prepare to fire an HTTP request
		url = 'http://wordpress.org/%s' % filename	
		response = urllib2.urlopen(url)
		f = open(filename, 'w')

		print 'Downloading: %s' % filename

		# Download the core in chunks of 8K
		while True:
			buffer = response.read(8192)
			if not buffer:
				break

			f.write(buffer)

		f.close()

		print 'Extracting: %s' % filename

		# Load the tar file, extract all files
		tar = tarfile.open(filename)
		tar.extractall()
		tar.close()
		
		# Remove the archive file
		os.remove(filename)
		
		# Let's see if --dir-name was specified, props to TomBlockley (IRC)
		if '--dir-name' in self.options:
			os.rename('wordpress', self.options['--dir-name'])
			
		return True
		
	def help(self):
		"""
		Command line help utility, will print out whatever is passed
		in as a second argument, or the general CLI help docs.
		"""
		pass
		
	def config_dir(self):
		"""
		Returns the directory of the configuration file (wp-config.php)
		if one is found, otherwise raises an Exception.
		"""
		current_dir = os.getcwd().split('/')
		while True:
			config_file = '/'.join(current_dir) + '/wp-config.php'
			if os.path.exists(config_file):
				break

			current_dir = current_dir[:-1]
			if len(current_dir) < 1:
				raise Exception('Could not locate WordPress, make sure a wp-config.php file is present.')

		return '/'.join(current_dir)

def main():
	cli = WordPressCLI()
	cli.execute()
	
def rm_rf(d):
	for path in (os.path.join(d,f) for f in os.listdir(d)):
		if os.path.isdir(path):
			rm_rf(path)
		else:
			os.unlink(path)
	os.rmdir(d)

if __name__ == '__main__':
	main()