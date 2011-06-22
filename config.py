#!/usr/bin/env python
import re
	
def loadOptions():
	global wp_config
	wp_config = []
	file = open("wp-config.php")
	for line in file:
		wp_config.append(line)
	
def getOption( name ):
	
	# load wp-config.php into wp_config if it doesn't exist
	# this only happens one
	global wp_config	
	try:
		wp_config
	except NameError:
		loadOptions()

	expression = re.compile( r"define\(\'"+name+"\', '(.*?)'\)" )
	for line in wp_config:
		m = expression.findall( line )
		if m:
			break
	return m[0]
	

# usage
print getOption('DB_HOST')
print getOption('DB_PASSWORD')
	