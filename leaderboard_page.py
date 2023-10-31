from bottle import route, template, default_app, request, static_file

def convert_seconds_to_duration(seconds):
	"""
	Takes an int, seconds, and returns a formatted string representing the readable time
	"""
	
	years, seconds = divmod(seconds, 31536000)
	days, seconds = divmod(seconds, 86400)
	hours, seconds = divmod(seconds, 3600)
	minutes, seconds = divmod(seconds, 60)
	duration = ""
	units = 0
	if years:
		duration += f"{years}y "
		units += 1
	if days:
		duration += f"{days}d "
		units += 1
	if hours and units < 2:
		duration += f"{hours}h "
		units += 1
	if minutes and units < 2:
		duration += f"{minutes}m "
		units += 1
	if seconds and units < 2:
		duration += f"{seconds}s "
		# units += 1 # not needed
	return duration

@route("/favicon.ico")
def serve_favicon():
    return static_file("LogoSponsorBlockSimple256px.png", root="./")

@route("/leaderboard")
def leaderboard():
	"""
	Generates the formatted webpage containing the leaderboard
	"""
	
	if (sort_on := request.query.sort) not in ["Submissions", "Skips", "Time"]:
		sort_on = "Submissions"

	path = "leaderboard.csv"

	# csv columns = Username, Submissions, Total Skips, Time Saved
	with open(path, "r") as f:
		rows = f.read().splitlines() 

	sort_nums = {"Submissions":1,"Skips":2,"Time":3,} # the column number to sort on

	users = [row.split(",") for row in rows]
	users.sort(key=lambda x: int(x[sort_nums[sort_on]]), reverse=True)

	position = 1
	for user in users:
		user[1] = f"{int(user[1]):,}"
		user[2] = f"{int(user[2]):,}"
		user[3] = convert_seconds_to_duration(int(user[3]))
		user.append(position)
		position += 1

	users = users[:200] # in leaderboard.py we only get the 200 highest users in any given category.

	return template("./leaderboard_template", users=users)

application = default_app()

if __name__ == "__main__":
	# run the server listening on localhost:8080
	host = "localhost"
	port = 8080
	application.run(host=host, port=port)
