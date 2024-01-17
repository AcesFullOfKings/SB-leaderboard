import os
import platform
from time import time
from datetime import datetime, timedelta
from contextlib import suppress
from daily_task import log

current_platform = platform.system()

if current_platform == "Darwin":  # macOS
	archive_location = "download/archive"
elif current_platform == "Linux":
	archive_location = "/mnt/whitebox/download/archive"
else:
	raise ValueError(f"Unknown platform: {current_platform}")


log("Deleting old database versions..")

today = datetime.now()

def days_since(date_string):
	return (datetime.now() - datetime.strptime(date_string, "%d%m%Y")).days

try:
	for filename in os.listdir(archive_location):
		file_day   = int(filename[0:2])
		file_date  = filename[0:8]

		file_age = days_since(file_date)

		if file_age >= 7 and file_day != 1:
			if file_age > 28:
				os.remove(archive_location + "/" + filename)
			else:
				if file_day % 7:
					os.remove(archive_location + "/" + filename)
except OSError as ex:
	log("Could not update archive - " + str(ex))

compressed_segs_local_path = f"download/sponsorTimes.csv.zst"
compressed_names_local_path = f"download/userNames.csv.zst"

with suppress(Exception):
	os.remove("download/old_sponsorTimes.csv")

with suppress(Exception):
	#move current file to "old"
	os.rename("download/sponsorTimes.csv", "download/old_sponsorTimes.csv")


log("Curling segs..")
os.system(f"curl https://sb.minibomba.pro/mirror/sponsorTimes.csv.zst --output {compressed_segs_local_path}")

log("Curling names..")
os.system(f"curl https://sb.minibomba.pro/mirror/userNames.csv.zst --output {compressed_names_local_path}")

log("Decompressing segs..")
# (requires brew install zstd)
cmd_segs = f"zstd -d -f {compressed_segs_local_path}" # decompress the file
os.system(cmd_segs)

log("Decompressing names..")
cmd_names = f"zstd -d -f {compressed_names_local_path}" # decompress the file
os.system(cmd_names)

log("Cleaning up compressed files..")
os.remove(compressed_segs_local_path) # remove the compressed files
os.remove(compressed_names_local_path)

if (not os.path.isfile("download/old_sponsorTimes.csv")) or ((new_size := os.path.getsize("download/sponsorTimes.csv")) > (old_size := os.path.getsize("download/old_sponsorTimes.csv"))):
	with open("last_db_update.txt", "w") as f:
		f.write(str(round(time())))
		
	with suppress(Exception):
		os.remove("download/old_sponsorTimes.csv")

	segs_filename_uncompressed = "sponsorTimes.csv"
	names_filename_uncompressed = "userNames.csv"

	log("Copying today's database to the archive..")
	today_string = today.strftime("%d%m%Y")
	try:
		os.system(f"sudo cp download/{segs_filename_uncompressed} {archive_location}/{today_string}_{segs_filename_uncompressed}")
		os.system(f"sudo cp download/{names_filename_uncompressed} {archive_location}/{today_string}_{names_filename_uncompressed}")
		os.system(f"sudo cp leaderboard.csv {archive_location}/{today_string}_leaderboard.csv") # this file hasn't been updated yet!
	except OSError as ex:
		log("Could not copy files to archive - " + str(ex))
else:
	log(f"Downloaded sponsorTimes.csv is SMALLER than the current file. (new_size is {new_size:,}; old_size is {old_size:,}). Ignoring it.")
	os.remove("download/sponsorTimes.csv")

	with suppress(Exception):
		#put the "old" file back as the current file
		os.rename("download/old_sponsorTimes.csv", "download/sponsorTimes.csv")

	#this exception should cause the result value to be nonzero, stopping the rest of the daily_task process.
	raise RuntimeError("New file is not bigger than old file. Aborting. Archive skipped.")

