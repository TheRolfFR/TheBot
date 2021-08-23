

def convert_dhms(duration):
	duration = int(duration)
	return (duration // 86400, (duration // 3600) % 24, (duration // 60) % 60, duration % 60)

def convert_dhms_string(duration):
	res = convert_dhms(duration)
	string = ''

	# days
	if res[0] != 0:
		string += str(res[0]) + ':'

	# hours
	if res[0] != 0 or res[1] != 0: # if days not null or hours not null
		if res[0] != 0: # if days not null
			string += '{:02}'.format(res[1]) # two digit hour
		else:
			string += str(res[1]) # min digit hour

		string += ':'

	# minutes
	if res[0] != 0 or res[1] != 0: # if days not null or hours not null
		string += '{:02}'.format(res[2]) # two digit minutes
	else:
		string += str(res[2]) # min digit minutes

	#seconds
	string += ':{:02}'.format(res[3])

	return string