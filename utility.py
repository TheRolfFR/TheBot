

def convert_dhms(duration):
	duration = int(duration)
	return (duration // 86400, (duration // 3600) % 24, (duration // 60) % 60, duration % 60)