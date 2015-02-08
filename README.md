# NBA-data-tool
This is an older data tool I used to scrape and clean NBA data. I've mostly moved on from this to better tools. There is a fair bit of documentation in the file itself - every function should have a little blurb. As a brief tour of some useful functions:

get_gamebooks: Given starting and ending date, this collects pdf gamebooks from nba.com. These are one of the few resources you can find online that give the names of each starter for each quarter. Most sites only tell you who the 1st quarter starters are. This can make it difficult to identify all players on the court. Unfortunately, using the gamebooks has its own pitfalls. Specifically, names in the gamebooks are sometimes different from names in play-by-plays, and there are no unique identifiers like the stats.nba.com player id to use. So you have to implement a bunch of kluges, like using the Levenshtein distance to try to decide if J. Cole and James Cole are the same person etc... This issue is why I ultimately abandoned this set of tools.

get_draft_data: This scrapes a bunch of career data for players and where they were picked in the draft. It was used in this blog post: http://austinclemens.com/blog/2014/02/22/should-you-trade-spencer-hawes-for-two-second-round-draft-picks/  I think it still works but you might want to spot-check for errors - as I recall there were some bugs in the future per numbers it picks up.

scrape_shots: I initially used this to get shots for my shot charts. It's pretty straight forward - grabs shots from NBA's api and writes out csvs. 

dleague_scrape_shots: Same thing for the D-league.

create_shot_csv: This was how I initially created the pre-processed data for shot charts. It returns x/y coordinates with number of shots, weighted FG% and etc.

goldsberry_allyears: Yeah ok I named my function after Kirk. This just takes a csv with all shots since 1996 in it and spits out tons of pre-processed shot chart csvs.

NCAA functions: theoretically these collect shot data for NCAA players. They may have to be changed - I'm not sure if they remain specific to the one year I scraped.

Most of the rest of the file is not that interesting... I wrote lots of functions in this file for specific use cases when I needed something for an article or whatever. My initial stab at Adjusted Defensive Impact is in here but I'm not sure what state it is in.



