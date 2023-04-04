# Schedule Parser

This was the first large scale project I made outside of school. Its purpose is to send front desk workers at UCLA's De Neve Front Desk and Evergreen Front Desk their individual schedules for the next week, as well as a personalized and private ics links that would subscribe them to a calendar that would update their shifts. 

This project uses pandas as a way to store and extract data from the schedules. I learned MIME, smtplib, and datetime for this project to create the calendar events for the ics file. I also spent weeks experimenting with Google Cloud to find a way to run this automatically and to find a way to link google sheets with gmail. This script is meant to be run in Google Colab. No GPU is necessary.

I made this schedule parser alone and without any help, so there are a lot of bad practices here and things are very messy. However, attribute this to the fact that the structure of the schedule changed every week. I also had to cover two different structures of schedules (one from Evergreen and one from De Neve). Moreover, workers were added every week, so I would have check and create new ics links for them to be included in this schedule sender. Finally, I would also have to check for typos any of the managers would make.

This readme will provide documentation of the structure of the Jupyter Notebook and the TODO's I want to implement in the future, in case anyone else would like apply this to their job as well. However, these are fitted to match the general structure of the schedules I had during my time working the front desk at UCLA. Thus, it may be best to just be inspired by this code and write a program from scratch with references to how this is organized.



## Structure

I'll go over the structure here.

### Spreadsheet Tab Names
The spreadsheets that were sent came as a new tab in an existing Google spreadsheet (for Evergreen, truncated to E for convenience) or as a new Google spreadsheet (for De Neve, truncated to N for convenience).

### Imports and Hidden Stuff
Here, I import all the libraries we need and define needed functions (like removing spaces at the end of a person's name). I also define the system of organizing hours and days to schedule calednar events and determine how long a shift is (it is bad, see the TODO section for more information on why). 

### Auth
This section asks for permission to access google drive, google spreadsheets, and google calendar. This part is important for getting the necessary credentials to send emails. Originally, I was going to implement a connection to the Google Cloud API to make this system automatic (and be able to access google sheets to find updated schedules), but I deemed it would be bad practice to do this, as I wanted to make sure the code would work as expected every time.

### Deconstruct Spreadsheets
This section specfically breaks down each structure of the respective schedules for Evergreen, De Neve, and De Neve special shifts. The formats were constantly changing and messy, which led to the code to deconstruct them being messy. There were some tests to ensure all front desk workers were accounted for. However, I would like to implement a better way of deconstructing these sheets in the future (see TODO section for more information).

Worker information was also zipped and stored to make sending emails easier.

### Add to Calendar and Send Email
These are just helper functions that reset the ics calendar for the week, add events to the ics calendar, and format a personalized email message notifying the worker of their shifts. The google calendar API was used to add the event to each worker's personalized ics calendar.

### Main
This is the main body that takes the worker information and the workers shifts and uses that to send them the personalized email and ics file. I made sure to not send emails if they weren't working that week. This system is not parallelized, but can be made to be (see the TODO section for more information).

### Troubleshooting
I ran into a lot of bugs due to the variablity of the structure of the schedules. Thus, I had to have a dedicated section for debugging code. This block specficially does not send emails and only edits the calendar. Usually, this was the case (as emails were usually robust to most changes, but their calendar equivalents were not) (see the TODO section for more information).



## Important things TODO

As this project scaled, there are many things I would like to do differently. Unfortunately, due to classes, I do not have time to redo this project or create the necessary changes to make this code more efficient/readable. I may come back to this project in the future to create a more robust system.

### Change time blocks system
Due to how scheduling changed over the course of my time work at UCLA's front desks, the system for days and hours needs to be dramatically improved. I had to adapt as 2:45 increments were added and taken away from the schedule (which still had to be considered a full 3 hours). 

Next time, I want a system that can specify whether to round or keep the minute details in the schedule.

### Parsing Spreadsheets
Due to the structuring of the spreadsheets, I had to find a very specific way to parse the schedules. Thus, I would change the code often to account for the way the spreadsheets changes. The biggest flaw for this system is that it parses the entire schedule each time it sends an email. Originally, this was because I didn't want to accidentally include a bug that would affect everyone and I'd have to resend emails/redo the calendar. Instead, I wanted a system that I could debug more easily and quickly adjust code on the fly to fix bugs.

Next time, I hope to make a more robust algorithm to detect schedules, differentiate names, and recognize additional information appended to each shift. This would allow me to run it on any schedule and still get the information needed to send the email and calendar events. More importantly, I hope to create a system that parallelizes gathering schedule information and add unit tests to alert me of any bugs before emails go out.

### Datetime
Due to the way UCLA's front desk schedules are formatted, I had to convert everything to datetime. I overfit this to UCLA's date format, so it's a bit convoluted.

In the future, I hope to remake this to make it more streamlined and readable.

### Add more config files
I originally had all of the ics links stored in the jupyter notebook itself. In retrospect (a few months after making this notebook), I realize how bad of an idea this is.

If I had the time, I would fix many places that need to have a config file storing the information.