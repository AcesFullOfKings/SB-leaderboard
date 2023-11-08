"""
sponsortimes.csv: videoID,startTime,endTime,votes,locked,incorrectVotes,UUID,userID,timeSubmitted,
				  views,category,actionType,service,videoDuration,hidden,reputation,shadowHidden,
				  hashedVideoID,userAgent,description
				  16.7M rows

usernames.csv:    userID,userName,locked
				  315k rows
"""

import csv
from time import time

start_time=time()

# set up segs reader:
sponsortimes = open("download/sponsorTimes.csv", "r")
first_row = sponsortimes.readline() # discard this so it's not processed in the loop below
del first_row

sponsortimes_field_names = ["videoID","startTime","endTime","votes","locked","incorrectVotes","UUID","userID","timeSubmitted","views","category","actionType","service","videoDuration","hidden","reputation","shadowHidden","hashedVideoID","userAgent","description"]
segment_reader = csv.DictReader(sponsortimes, fieldnames=sponsortimes_field_names)


#set up users reader:
usernames = open("download/userNames.csv", "r")
first_row = usernames.readline() # discard this so it's not processed in the loop below
del first_row

usernames_field_names = ["userID","userName","locked"]
username_reader = csv.DictReader(usernames, fieldnames=usernames_field_names)

users = dict() # format -> {userID:{username:"", submissions:0, skips:0, time_saved:0},}
line_num = 0

print("Processing sponsorTimes.csv..")

for segment in segment_reader:
	votes        = int(segment["votes"])
	hidden       = int(segment["hidden"])
	shadowHidden = int(segment["shadowHidden"])
	endTime      = float(segment["endTime"])
	startTime    = float(segment["startTime"])
	views        = int(segment["views"])
	userID       = segment["userID"]
	actionType   = segment["actionType"]

	# don't count removed/hidden submissions
	if ((votes > -2) and (not hidden) and (not shadowHidden) and (actionType=="skip")):
		duration = endTime-startTime

		if userID not in users:
			users[userID] = {"submissions":0, "total_skips":0, "time_saved":0, "username":userID}

		users[userID]["total_skips"] += views
		users[userID]["time_saved"]  += (duration*views)
		users[userID]["submissions"] += 1

	line_num += 1
	if not line_num%1000000:
		print(f"Processing line {line_num}")

sponsortimes.close() # finished with this file now
end_time=time()

print(f"Time taken: {round(end_time-start_time,1)}")
print("Processing usernames.csv..")

line_num=0 # only for printing progress

for user_row in username_reader:
	userID    = user_row["userID"]
	user_name = user_row["userName"]
	#locked    = user_row["locked"]

	if userID in users:
		users[userID]["username"] = user_name
	
	line_num += 1

	if not line_num%100000:
		print(f"Processing user {line_num}")

usernames.close() # finished with this

#convert dict to list of lists (for easier sorting below)
user_list=[]
while users:
	user_id, user_info = users.popitem() # returns and deletes the next item from users as a tuple of (key, value)
	user_tuple = (user_id, user_info["username"], user_info["submissions"], user_info["total_skips"], user_info["time_saved"])
	user_list.append(user_tuple)

del users

top_submissions = sorted(user_list, key=lambda x: x[2], reverse=True)[:200]
top_skips       = sorted(user_list, key=lambda x: x[3], reverse=True)[:200]
top_time_saved  = sorted(user_list, key=lambda x: x[4], reverse=True)[:200]

del user_list

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
		user_id     = user[0]
		username    = user[1].replace(",", "") # no commas, bad
		submissions = user[2]
		skips       = user[3]
		time_saved  = round(user[4])

		f.write(f"{user_id},{username},{submissions},{skips},{time_saved}\n")

		line_num += 1
		
		if not line_num%100:
			print(f"Writing line {line_num}")

print("Done!")
