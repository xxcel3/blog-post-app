# cse312project
CSE312 project link -> hobbied.bond


For Project Part 3, Objective 3, we added a functionality for resetting password. Users would be able to reset their password if the username is in the database and the old password matches with the current password.
There will be an error message if the username is not in the database or the old password is incorrect and there will be a success message if otherwise. 
The testing procedure is below:

1) Start your server with "docker compose up"
2) Open a browser and navigate to http://localhost:8080/
3) Register an account in registration form
4) Login with account to verify this username and password then logout
5) Attempt to reset passwords with wrong username
7) Attempt to reset passwords with wrong old password
8) Reset correct username and correct old password with a new password
9) Login with account to verify this username and the new password

For Project Part 3, Objective 1, is a 10 second timer quiz with scoreboard of submitted users.