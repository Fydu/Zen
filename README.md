ZEN - Track your daily calories
#### Video Demo: https://youtu.be/zQIKkdPqp7g
#### Description:
This is my final project for Harvard's CS50 made with HTML, CSS, Javascript, Flask, Jinja and SQL.
It's a web-based application that allows you to track your daily caloric intake, as well as decide how much you should eat based on your goals.
I felt inspired to work on this because, near the end of the course, I started tracking my calories and had to search for a tool to do so.
I worked on this project for about 2-3 weeks, and beforehand I had decided to take some more online courses and watch some tutorials to reinforce my CSS knowledge (such as freeCodeCamp's)which really came in handy.

#### LANDING
Here i tried to make a simple landing with a motivational line and a Get Started button, nothing too fancy but an animated background that i thought looked nice.

#### REGISTER
In the registration process, there are multiple steps, first we get to choose our username and password.
This is a separate step because i wanted to check for username availability without having the user complete a whole form filled with personal info (such as age, sex, weight, height)
and then realizing "Oh, that username already exists/Oh, that password is too short" and having to fill it out again.
Next step leads you to /profile-setup which you can't avoid, it's necessary and can't go to any other page without completing it first.
Here, you will provide the App with all the necessary information to calculate your daily caloric intake and macros according to your goals.

#### HOME DASHBOARD
Once you completed your profile setup, you will be greeted with the home dashboard, which will present you the following:
-Calories consumed so far and % of calories consumed
-Daily caloric goal
Then, you will have three buttons which will lead you to the following pages

#### DIARY
Here, you will be able to see all of your meals, their calories, their names, and date.
You are able to choose a prior/future date to see that day's entry in your diary, they will all be empty at first, but you will be filling them out eventually.
You can also delete your meals in this page.

#### ADD MEAL AND ADD FOOD
You are able to add a meal to your diary, and choose a date for that meal (if empty it will automatically choose today)
And withing the /add-meal you have a + button which will allow you to input a new food item, declaring it's calories and macros per 1 unit / 100g / 100ml.

#### SETTINGS
Let's say your daily activity changes due to you having a different job, or starting a new workout routine. Or even you decide to change objectives and now you want to gain weight instead
of mantaining, well, in settings you can modify all of your data.
Leave blank all the options you want to remain unchanged and make sure to submit via the "Save changes" button.

#### ABOUT
Here i talk about the project and myself.

Special thanks:
-freeCodeCamp's Responsive Web Design Certification
-WebStylePress Floating Cubes Animated Background
-dotWebDesign's Awesome Responsive Multi Step Registration Form
-ProgProd's easyPieChart tutorial