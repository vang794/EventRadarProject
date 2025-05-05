# Testing Plan  

## Group 1 - Event Radar 

Annalise Harms, Benjamin Hackbart, Carolyn Vang, Jannatul Hakim, Jonny Leston 

April 20, 2025  

## Team Information 

If you have any questions or need assistance, please email us at eventraderofficial@gmail.com. 

## System Overview 

Event Radar is a website for travelers and active locals looking to explore local activities, connect with others, and explore what their community has to offer. Users can access weather, parking lot locations and more information to help assist in planning. Users can also apply to be an event manager, giving them the ability to create and post events on platform. Users can add events to their personal schedule to save events and help plan for upcoming trips. Event Radar simplifies event planning by keeping all the key details in one place. 

## Access Instructions 

1. Link to GitHub repository  

   [https://github.com/vang794/EventRadarProject.git](https://github.com/vang794/EventRadarProject.git)

2. Requirements 

   a. Python 3.10 or higher  
   
   b. Django 5.x  
   
   c. MySQL Server  
   
   d. MySQL Client  
   
   e. PyCharm or Visual Studio Code  

3. Instructions to install and run the project 

   a. Clone Project Repository

      ```
      git clone https://github.com/vang794/EventRadarProject.git
      ```

   b. Navigate to Project Directory

      ```
      cd EventRadarProject
      ```

   c. Create a file named ‘.env’ in folder EventRadarProject (same level as settings.py) and input the following text:

      ```
      DB_NAME = EventRadar  
      DB_USER = admin  
      DB_PASSWORD = [refer to Testing Plan document for DB Password]
      DB_HOST = eventradar.chqo2mui2hfr.us-east-2.rds.amazonaws.com  
      DB_PORT = 3306  
      SENDGRID_API_KEY = [refer to Testing Plan document for API key]
      ```

   d. Set Up Virtual Environment

      ```
      python -m venv venv
      source venv/bin/activate
      ```

   e. Install Dependencies

      ```
      pip install -r requirements.txt
      pip install python-dotenv mysqlclient
      ```

   f. Apply Migrations

      ```
      python manage.py makemigrations
      python manage.py migrate
      ```

   g. Run Server

      ```
      python manage.py runserver
      ```

4. Login Credentials  

   a. Normal User Login 

      i. Email: EventRadarOfficial@gmail.com  
      
      ii. Password: Test123!  

   b. Event Manager Login 

      i. Email: EventRaderOfficial@gmail.com  
      
      ii. Password: Manager123!  

## Test Scenarios 

### a. Create an event 

   i. Login as an event manager  

   ii. Press ‘manage events’  

   iii. Fill in information for an event based in Milwaukee  

   1. Address: 611 N Broadway, Milwaukee, WI 53202  
   2. Make sure date is set to current date or later  

   iv. Press ‘create event’  

   v. Navigate back to homepage  

   vi. Make sure the dates at the top of the homepage matches dates entered for the new event created  

   vii. Confirm event you created are present in list of all events  

### b. Add events to personal schedule plan 

   i. Login as an event manager  

   ii. Press ‘manage plans’  

   iii. Press ‘create a plan’  

   iv. Enter relevant information then press ‘create plan’  

   v. Navigate back to homepage  

   vi. Type in “Milwaukee”, desired radius, start date and end date. Check any categories that you want to see and click search.  

   vii. Scroll through events and add a few to your plan by clicking on event and pressing ‘add to plan’  

   viii. Press ‘view my plans’ on the top of the homepage  

   ix. Select the plan you created  

   x. Confirm all events you previously added are present  

## Optional Test Scenario 

### a. Change account details  

   i. Login as either event manager or normal user  

   ii. Press ‘settings’  

   iii. Change email address then press ‘update email’  

   iv. Scroll to bottom of setting page and press ‘logout’  

   v. Log in again with your new email address to confirm the update  
