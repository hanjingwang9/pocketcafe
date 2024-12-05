# Pocket Café

Pocket Café is an all-in-one platform for coffee lovers at Harvard. 

## Video Introduction

https://youtu.be/i7jzsw-cWMM

## Installation

To run Pocket Café on your device, download the `.zip` file containing all files in this project and navigate to the `pocketcafe` directory on your terminal.

Please check `requirements.txt` for required packages. Alternatively, run the following:

```bash
pip install -r requirements.txt
```

Then, you can start running the app locally with the command:

```bash
flask run
```

## Usage

Pocket Café has three main features:
- Logging entries;
- Searching for coffee drinks; 
- Creating personalized, shareable coffee name cards. 

It supports multiple users/accounts, provided that each user has a unique username. 

To start, register for an account with a unique username. After registration, you will be directed to a personalized homepage where you can access all features of the app.

## Disclaimers

Pocket Café primarily serves the population at Harvard, so its menu database is limited to regularly available drinks at coffee venues based in Harvard Square.

Please note that the search function utilizes the free version of Unsplash's API, which limits the number of queries per hour to 50. If you search for a large amount of drinks within a short time-frame, your search results might temporarily lack reference photos. This is a normal occurence and does not affect the accuracy of your results. 

## Support

For any questions or issues with installation/usage, please contact <hanjingwang@college.harvard.edu>.

