# Automated-ArcReader-Update
Here's the start of a python program to automate the copy &amp; export of an SDE geodatabase for use in disconnected (no internet access) remote laptop environment. Replication of the SDE geodatabase was not an option since the entire database was too large; therefore we needed to select a subset of all feature datasets and feature classes to copy into a PortableDuluth.gdb. This python program also automates copying, clipping, &amp; export of parcel layers for ownership. The script creates a track log of all procedures completed with logging any errors as well as gives a script runtime. 

# NEED FOR ARCREADER UPDATING PROJECT:
All field workers with laptops currently use the ArcReader map “TapNCurb” and need a current copy of our in-network SQL Server SDE GIS Database with new utilities, ownership, & GPS points. They sometimes have spotty internet connection and thus need a reliable disconnected map solution to view updated utility and ownership data as soon as new data are available to help them locate the City’s utilities for Gopher State One Calls.

# OBSTACLES TO OVERCOME:
The map has normally only been updated every ~1-3 months depending on when the field worker connects their laptop to the City Network AND Mick Thorstad has updated the database holding all the GIS data for the map. The GIS database has been an exported copy of the SQL Server SDE GIS database that Richard and Al manage. In the past, Mick has exported all the tables needed for the remote database every 1-3 months since it takes him 1-2 days to complete the database export process manually; it’s a lengthy and annoying manual update process.

#PROPOSED SOLUTION:
#1.	Automate remote database export of GIS database
#2.	Update the batch script that field workers run to copy the new remote database and TapNCurb.pmf map onto their laptops
#3.	Work with IT to add a pop-up message on field worker’s laptops that informs them if their database & map is more than 1 week old (& hopefully encourages them to update the map ASAP).
#4.	In the future…Work with IT to possibly “push” the ArcReader map & database updates to remote worker’s laptops, so field workers don’t need to always bring their laptops into the office.
