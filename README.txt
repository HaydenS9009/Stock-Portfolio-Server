For this assignment we were given a basic python server, and had to create a stock portfolio web application. The basic python server here (server3.py) is extended 
well beyond the original file. Anything not related to the basic function of handling connections of a python server was written by me (Hayden Stimpson).

The main functionality of this web application is in portfolio.html and research.html.
portfolio.html displays a table where stocks can be added and removed, and a table displaying any previously added stocks. 
research.html has a search bar, when a stock symbol is entered here the basic information about the stock and the five year stock chart will appear. 

This is all connected with the server, which allows permanent storage of stocks you have added through the portfolio.xml file. 

The server was originally built to require a password and username, but now will not ask for one. This can be reimplemented on line 204 in server3.py 
by removing the "or y = ''" and replacing the authentication code with the browser authentication code for your wanted username and password. This code can be found
while having the browser network developer tools open, then submitting your wanted username and password into the popup. The website will deny access, but in the latest
entry in the network developer tools, find the request header saying 'Authorization: Basic '. The code following this can replace my code on line 204,
and then the website will accept your username and password and allow access to the site. 
