INTRODUCTION
------------

This is a WebApp developed for EVAC admin and EMTs to use on a regular basis. Created by Emma Millet, Alyssa Nguyen, and Isabel Ting
for the 2021-2022 Capstone project at Bergen County Academies. This WebApp includes multiple forms for EMTs to fill out (rig-check,
clock in, shift sign-up, user editing), user info and management, a calendar to view taken shifts, and a differentiation between
admin and general EMT users for data access.

REQUIREMENTS
------------

Python (3.0 onwards)
SQL and MySQL Workbench --> database configuration
Auth0 --> user management, creation, and admin
Flask (including Flask-Mail & Flask-MySQL)--> Python WebApp creation
Heroku --> Hosting (Optional, may be hosted on another hoster entirely)
JawsDB --> For connecting SQL Database to the app

Please refer to requirements.txt for more information for specific installations that may be accomplished using the pip terminal command.

CONFIGURATION
-------------
 
Refer to SQL folder to find SQL files that you may use to create a new database. 
Connect the database using JAWSDB and Heroku. 
Host and Deploy onto Heroku after properly connecting the database to the Flask app. (Use the Git CLI - installable online)
    * Ensure to change the .env file details for the new database connection.
Setup Auth0 using a new account and change the URL in the app.py file when initiating Auth0 to reflect the new address of the site chosen.
    * Ensure to change the .env file details for the new Auth0 client connection. 
