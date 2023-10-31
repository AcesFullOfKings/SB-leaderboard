"""
sponsortimes.csv: videoID,startTime,endTime,votes,locked,incorrectVotes,UUID,userID,timeSubmitted,
				  views,category,actionType,service,videoDuration,hidden,reputation,shadowHidden,
				  hashedVideoID,userAgent,description
				  16.7M rows

usernames.csv:    userID,userName,locked
				  315k rows
"""

sponsortimes = open("sponsorTimes.csv", "r")
first_row = sponsortimes.readline() # discard this so it's not processed int he loop below

users = dict() # format -> {userID:{username:"", submissions:0, skips:0, time_saved:0},}

line_num = 0

print("Processing sponsorTimes.csv..")
for line in sponsortimes:
	try:
		videoID,startTime,endTime,votes,locked,incorrectVotes,UUID,userID,timeSubmitted,views,category,actionType,service,videoDuration,hidden,reputation,shadowHidden,hashedVideoID,userAgent,description = line.split(",")
	except:
		#print(f"ignoring broken line on line {line_num}")
		#print(line)
		continue

	# don't count removed/hidden submissions
	if ((int(votes) > -2) and (hidden == "0") and (shadowHidden == "0") and 
		(actionType=="skip")):
		duration = float(endTime)-float(startTime)
		views = int(views)

		if userID not in users:
			users[userID] = {"submissions":0, "total_skips":0, "time_saved":0, "username":userID}

		users[userID]["total_skips"] += views
		users[userID]["time_saved"] += (duration*views)
		users[userID]["submissions"] += 1

	line_num += 1
	if not line_num%1000000:
		print(f"Processing line {line_num}")


print("Processing usernames.csv..")
usernames = open("usernames.csv", "r")

line_num=0

for row in usernames:
	try:
		columns   = row.split(",")
		userID    = columns[0]
		locked    = columns[-1]
		user_name = ",".join(columns[1:-1]) # bc sometimes the username contains commas which is a headache
		user_name = user_name.strip("\"")
	except ValueError:
		continue

	if userID in users:
		users[userID]["username"] = user_name
	
	line_num += 1

	if not line_num%100000:
		print(f"Processing user {line_num}")

#convert dict to list of lists (for easier sorting)
user_list = [[user_id, user_info["username"], user_info["submissions"], user_info["total_skips"], user_info["time_saved"]]
             for user_id, user_info in users.items()]

top_skips       = sorted(user_list, key=lambda x: x[2], reverse=True)[:200]
top_submissions = sorted(user_list, key=lambda x: x[3], reverse=True)[:200]
top_time_saved  = sorted(user_list, key=lambda x: x[4], reverse=True)[:200]

# Merge the users from each top list
added_userIDs = set() # so we don't add a user more than once
top_users = list()

for user in top_skips:
	if user[0] not in added_userIDs:
		top_users.append(user)
		added_userIDs.add(user[0])

for user in top_submissions:
	if user[0] not in added_userIDs:
		top_users.append(user)
		added_userIDs.add(user[0])

for user in top_time_saved:
	if user[0] not in added_userIDs:
		top_users.append(user)
		added_userIDs.add(user[0])

print("Writing output to file..")
line_num = 0

with open("leaderboard.csv", "w") as f:
	for user in top_users:
		username    = user[1]
		submissions = user[2]
		skips       = user[3]
		time_saved  = round(user[4])

		f.write(f"{username}, {submissions}, {skips}, {time_saved}\n")

		line_num += 1
		
		if not line_num%100:
			print(f"Writing line {line_num}")

		#for testing: 
		#if line_num > 100_000:
		#	break
