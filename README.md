# ELSA_StatMeldr

ELSA StatMeldr is an application that makes fetching data easier.
It does this by fetching data from an external dataset, and storing all of that in a redis Cache.
The reason for the cachie is that it makes filtering the data easier.

At this moment the app supports CBS and RIVM databases. 

![githubpic](https://github.com/user-attachments/assets/8e3772b5-14c6-4c09-b616-3cce58f8f47f)


If CBS/RIVM changes their API calls, this is how i found out how to make them:
1) go to CBS/RIVM on statmelder and select a dataset you want to download
2) Pick a random filter for a municipality, then then prepare your web browsers developer tools
3) one of the tools can record all incomming/outgoing traffic, spot the GET your pc sends to the CBS/RIVM servers
4) This request is formatted like an URL, just change the symbol into what they're supposed to be, and then you got the api call, with a municipality filter.
