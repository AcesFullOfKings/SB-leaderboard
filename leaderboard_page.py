from bottle import route, template, default_app, request, static_file, request

def format_seconds(seconds):
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
	return static_file("LogoSponsorBlockSimple256px.png", root="/home/AcesFullOfKings/server/")

@route("/beta")
def serve_beta():
	if (sort_on := request.query.sort) not in ["Submissions", "Skips", "Time"]:
		sort_on = "Submissions"

	users = get_users(sort_on=sort_on)

	return template("/home/AcesFullOfKings/server/beta_page.html", users=users)


@route("/")
def leaderboard():
	if (sort_on := request.query.sort) not in ["Submissions", "Skips", "Time"]:
		sort_on = "Submissions"

	users = get_users(sort_on=sort_on)

	return template("/home/AcesFullOfKings/server/leaderboard_page.html", users=users)

def get_users(sort_on="Submissions"):
	if sort_on not in ["Submissions", "Skips", "Time"]:
		sort_on = "Submissions"

	path = "/home/AcesFullOfKings/server/leaderboard.csv"

	# columns = UserID, Username, Submissions, Total Skips, Time Saved
	with open(path, "r") as f:
		rows = f.read().splitlines() 

	sort_nums = {"Submissions":2,"Skips":3,"Time":4,}

	users = [row.split(",") for row in rows]

	users.sort(key=lambda x: int(x[sort_nums[sort_on]]), reverse=True)

	position = 1
	for user in users:
		user_id = user[0] #not displayed, only for the link
		username = user[1]
		length = len(username)
		if length > 20 and " " not in username:
			user[1] = username[:length//2] + "​" + username[length//2:] # zero-width space inserted
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

@route("/leaderboardStyleLight.css")
def css_light():
    return static_file("leaderboardStyleLight.css", root="/home/AcesFullOfKings/server/")

@route("/leaderboardStyleDark.css")
def css_dark():
    return static_file("leaderboardStyleDark.css", root="/home/AcesFullOfKings/server/")

application = default_app()

if __name__ == "__main__":
	application.run(host="localhost", port=8080)