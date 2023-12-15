from bottle import route, template, default_app, request, static_file, request
from datetime import datetime
import platform

current_platform = platform.system()

if current_platform == "Darwin":  # macOS
	file_location = ""
elif current_platform == "Linux": # cloud server
	file_location = "/home/AcesFullOfKings/server/"
else:
	raise ValueError(f"Unknown platform: {current_platform}")

del platform

def format_seconds(seconds):
	# a year is not defined in seconds, but for simplicity I use 365*24*60*60. good enough
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
	return static_file("LogoSponsorBlockSimple256px.png", root=file_location)

def get_last_updated():
    with open(file_location+"last_db_update.txt", "r") as f:
        last_update = f.read()

    formatted_string = datetime.utcfromtimestamp(int(last_update)).strftime('%d/%m/%y %H:%M')

    return formatted_string

@route("/beta")
def serve_beta():
	if (sort_on := request.query.sort) not in ["Submissions", "Skips", "Time"]:
		sort_on = "Submissions"

	users = get_users(sort_on=sort_on)
	global_stats = get_global_stats()

	print(global_stats)

	return template(file_location + "beta_page.html", users=users, global_stats=global_stats, last_updated=get_last_updated())


@route("/")
def leaderboard():
	if (sort_on := request.query.sort) not in ["Submissions", "Skips", "Time"]:
		sort_on = "Submissions"

	users = get_users(sort_on=sort_on)
	global_stats = get_global_stats()

	print(global_stats)

	return template(file_location + "leaderboard_page.html", users=users, global_stats=global_stats, last_updated=get_last_updated())

def get_users(sort_on="Submissions"):
	if sort_on not in ["Submissions", "Skips", "Time"]:
		sort_on = "Submissions"

	path = file_location + "leaderboard.csv"

	# columns = UserID, Username, Submissions, Total Skips, Time Saved
	with open(path, "r") as f:
		rows = f.read().splitlines()

	sort_nums = {"Submissions":2,"Skips":3,"Time":4,}

	users = [row.split(",") for row in rows]

	users.sort(key=lambda x: int(x[sort_nums[sort_on]]), reverse=True)

	position = 1
	for user in users:
		user_id = user[0] #not displayed, only used for the link
		username = user[1]
		length = len(username)
		if length > 20 and " " not in username: # good enough heuristic for long usernames which won't split over two lines
			user[1] = username[:length//2] + "​" + username[length//2:] # zero-width space inserted so it can span two lines
		user[2] = f"{int(user[2]):,}"
		user[3] = f"{int(user[3]):,}"
		user[4] = format_seconds(int(user[4]))
		user.append(position)

		if user_id == username:
			user.append(f"https://sb.ltn.fi/userid/{user_id}")
		else:
			user.append(f"https://sb.ltn.fi/username/{username}")

		position += 1

	users = users[:200] # in leaderboard.py we only get the 200 highest users in any given category.
	return users

def get_global_stats():
	with open(file_location+"global_stats.txt", "r") as f:
		file_data = f.read().split()

	global_stats = dict()
	global_stats["contributing_users"]  = file_data[0]
	global_stats["overall_submissions"] = file_data[1]
	global_stats["overall_time_saved"]  = format_seconds(int(float(file_data[2])))
	global_stats["overall_skips"]       = file_data[3]
	global_stats["removed_submissions"] = file_data[4]

	return global_stats

@route("/leaderboardStyleLight.css")
def css_light():
    return static_file("leaderboardStyleLight.css", root=file_location)

@route("/leaderboardStyleDark.css")
def css_dark():
    return static_file("leaderboardStyleDark.css", root=file_location)

application = default_app()

if __name__ == "__main__":
	application.run(host="localhost", port=8080)#, debug=True, reloader=True)
