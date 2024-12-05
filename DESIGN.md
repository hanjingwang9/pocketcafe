# Design Documentation

## Overview

As summarized in `README.md`, Pocket Café has 3 main features as well as several other supporting functions. This document will provide a general tour of all technical and stylistic elements of the project. It will touch on:

- Context
- Helper functions & databases
- Feature 1: logging coffees and viewing past entries
    - An extension of Feature 1 on the homepage
- Feature 2: searching for drinks around Harvard Square
    - The use of SQL databases to store café menus
    - The use of API for search results
- Feature 3: customizing a downloadable coffee name card
- Style and user interface

## Context

As an avid coffee drinker and journaling enthusiast, I've always wanted a place to log all the coffees I've had for later. I also knew that Harvard Square offered plethora of different coffee drinks from various chains, but there wasn't any way to systematically search through them. What if I created my own platform that allowed for users to jot down their coffee of the day? And what if they could conveniently search for their next cup, too?

Pocket Café expanded from this simple thought, ultimately growing into a full-fledged project with a much more complex set of features. My hope is that a coffee-lover (like me) can use this all-in-one app to revisit past memories, find future favorites, and share their joy with friends.

## Helper Functions & Databases

Much like what we did in `finance`, I started by writing a few helper functions in `helpers.py`. Two of them are familiar: the `login_required` function stayed the same, requiring the user to be logged in before accessing certain pages. The `apology` function also stayed relatively similar, although I found a more relevant meme of overflowing coffee to display error messages.

The new function I introduced was `fetch_images`, which takes the input of a drink name, queries it through Unsplash's API feature, and returns the link of the first image in search results (if exists). I had to play around with the exact query: having just the drink name and brand turned out to be too general and returned non-related images, so I ended up adding "coffee" at the end of the query. This made results much better. The function also returns `None` if the search does not yield anything (i.e. the user has exceeded Unsplash's API search limit). This way, other functions can more gracefully handle such an error.

The `login`, `logout`, and `register` functions in `app.py` also stayed relatively the same; however, my app also take note of a user's username when they log in, for a more personalized homepage. I improved upon my design by storing the user id and username after they register and automatically directing them to the homepage, rather than directing them to the login page again.

Corresponding to this is the `users` table in `cafe.db`, which notes the id, username (with `UNIQUE` attribute), and hashed password for each user. The user id was set to be auto-incremented for convenience.

## Logging

The biggest feature of Pocket Café is, as its name suggests, keeping a diary of the user's past coffees "in their pocket". Thus, I first spent my time creating a detailed, user-friendly logging tool that has three main aspects.

### Logging Page

The logging page is the first on the navbar, making it the first feature the user encounters. Upon clicking on the link (via `GET`), the user is prompted to fill out several aspects of their coffee: name, brand, roast, sweetness, rating, and description. Name and brand allow for text input, since there might be many brands and drinks that the user has tried. On the other hand, roast and sweetness are both select bars, since they are consistent across all coffees and make it easier for other functions to compute summary statistics.

The rating element took me a long time to make, since I wanted to include an engaging 5-star visual. In the end, I referred to an example by Vikas Choubey, arranging the stars in reverse in order to select "subsequent siblings" in CSS. I also added some JavaScript code to send the corresponding rating value to the Python function and prevent the user from submitting the entry without a rating. 

All other fields are also required in the HTML code and must be filled out before the user is able to submit (via `POST`). This is to ensure that the app's database does not have NULL values and run into errors. Just to be safe, I also included error handling in my `log` Python function in case a user tries to manually bypass the HTML constraints.

When a user successfully submits a new log, the `log` function appends a new row to a table named `logs` in `cafe.db`, which documents their user id, the contents of their log, and the date of their submission (in Eastern time) through the `datetime` library. When this is completed, they will be redirected to the homepage with a flash success message.

### Past Entries Page

The data behind the `entries` page is a subset of entries in the `logs` database that includes the current user's id. The `entries` function retrieves this data through a SQL query and sends it to the corresponding HTML page, which then displays them in an easy-to-read table.

The title includes the user's username as a personal touch. There's also an "add" button that links to the logging page, in case the user is reminded of a new entry when reading their previous entries.

### Homepage

The homepage is an extension of the previous two pages' data, creating a summary of the user's entries. This is done in two aspects.

The first is an SQL query that extracts count of entries and average rating of the user this week, with the help of SQL commands and `datetime`. This is then displayed at the center of the homepage, so that the user can easily see the number of coffees they drank (as well as how satisfied they were with those coffees) in the past week. This is again accompanied by a personalized greeting and a button to the logging page, in case the user realizes they forgot to log something.

The second element is retrieving the user's "top 5 cups of coffees" of the week, which is also done through an SQL query. After filtering for the user's id and the current week, my SQL query orders the results through descending rating, then recency (under the same rating). The final dictionary is limited to 5 entries, to control the size of the program. This is then passed to the homepage, which displays a summary of the very top entry. It's also stored as a global dictionary, as the namecard function will again use it.

There are convenient buttons located at the bottom right of the homepage that direct the user to the search and past entries pages, in case they have scrolled down and do not see the navbar.

## Searching

### Menu Database

The largest table in `cafe.db`, named `menu`, contains information about coffee-based drinks from 6 different coffee chains around Harvard Square. Besides each drink's name and brand, it also documents if it's espresso-based, available temperatures, and description. I made `espresso-based` boolean and `temperature` numeric (1 indicates hot only, 2 indicates iced only, and 0 indicates both) in order to simplify conditional statements in my other functions.

In total, there are 125 drinks documented in `menu`. I only included regular drinks, available year-round, that contained coffee. Each drink was entered manually; I recognize that this was probably more tedious than necessary, but I was unable to find an API tool that could systematically cover the menus of every coffee chain.

### Search and Result Pages

When the user clicks on the search page, they are given several options to refine their query. They can choose a brand, drink temperature, and type (espresso or non-espresso based), as well as enter any keywords that come to mind -- for example, "caramel" or "latte". The first three fields are all select bars, for convenience (and ability to control the entered values on the developer end). 

All fields are required, except for "keywords". In order to handle the case that the user does not include any keywords in their search, I structured my `search` function to first check its return value and assign a wildcard if the return value is `NULL`. From this, I initialize a SQL query and append additional constraints (with their corresponding parameters) if the user chose any specificities for `brand`, `temperature`, or `espresso`. I originally wrote a single query with all the parameters included, but found that the SQL search did not work in the case of constraints being `NULL`. Therefore, I changed the query to be dynamically sized, depending on user input.

The query returns a table of results, which is sent to the results page (where the user is also directed upon successful submission). This page was initially just a simple table containing the name, brand, and description for each result. However, this looked quite unengaging. Based on suggestions, I changed the page's layout to a grid of cards instead, which shows the coffee name and brand for each result. If the user was interested in a particular result, they can click the "View Description" button to learn more about that drink. This was achieved through Bootstrap's `modal` function and made the page much more interactive. 

I also wanted to include a reference image for each result, utilizing my `fetch_image` function. However, there was a problem: if the user searched too many times within a single hour (or their query had too many results), Unsplash's API would stop returning images. To account for this, I created a default card cover in `style.css` and improved my code to display this card cover in the case of no image.

Another limitation is that the reference images often repeated or were only tangentially related to the drink in question. This can probably be improved through using a more relevant API service (Unsplash photos are more general and from freelance photographers, not official companies such as Starbucks). However, I still found that having a reference image was helpful to the user and a good improvement stylistically.

## Namecard

The final feature of Pocket Café is more front-end focused, and intended as a tool for the user to share a part of their hobby with their friends (and hopefully share my app as well!) This takes the form of a customizable namecard that automatically downloads to the user's local drive.

There are 3 custom elements to the namecard: their username, a favorite drink, and a favorite brand/café to hang out. I made the favorite drink a select menu, with the options being the user's weekly top 5 drinks (found when the homepage is rendered). This makes the namecard feature more connected to Pocket Café's other features, and encourages the user to log their favorite coffees instead of just manually entering them on this page.

However, I made the "brand" element a text input, since I thought that some brands/cafés are not necessarily included in my databases but could be favorite spots for the user (and they might not have gotten a coffee there in the past week).

In order to make the user's choices appear on the namecard in real time, I added JavaScript listeners to the input fields and pasted the user's inputs onto pre-designated `span`s on the namecard. Then, when the user is ready and clicks "Capture", I wanted their browser to automatically download their namecard onto their device.

This was achieved through a helpful package, `html2canvas`, created by Niklas von Hertzen. I used an open source version of the package in order to minimize the size of my app overall. However, the package only converts the HTML and CSS code into information on a canvas, and does not necessarily render an image. Using JavaScript, I turned this information into an image URL and activated it for download on "click".

I also ran into the issue that the created image, alongside its image URL, would show up on the webpage when the download occurs. This disrupts the overall design and user-friendliness of the page, as the user would need to reload to get rid of it and make further edits to the namecard. I solved this by removing the image and image URL at the same time of the download, through JavaScript.

## Style and User Interface

I wanted my app to feel personal and cozy; a cup of coffee is, after all, something that warms us and wakes us up on a cold day. This feeling of peace, comfort, and familiarity was my overarching goal when making design-related choices throughout the project.

The color palette is set to a muted green, creating a calm atmosphere that eases the eye. User text selection, buttons (as well as hover colors), headers, and cards are consistent with this color palette. All webpages have a cream background to match the green accents.

The font is set to Gill-Sans, which combines the modern look of professional websites with a heavier text-weight associated with typewriters (consistent with the logging features of this app). I also used Futura for some accents, which is compatible stylistically with Gill-Sans but has slightly more angular look.

The main icon/visual for the app is a coffee cup favicon, which is shown site-wide on the navbar, as the tab icon, and on the namecard specifically. In order to add more engaging visuals (but still keep the website relatively minimalistic), I added a steaming coffee GIF at the center of the homepage. This creates a cozy atmosphere right as the user logs in, but also naturally separates their summary statistics in an intuitive way.

Cards and container boxes utilize shadows to give the website a more realistic feel. Similarly, the namecard had the aim of resembling a real-life "business card", so I tried to recreate its dimensions. The design of the namecard is also simplistic, with simple borders and hearts that echo the homepage in order to increase the overall app design's consistency.