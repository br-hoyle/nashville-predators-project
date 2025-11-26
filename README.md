# Nashville Predators Assessment
Benjamin Hoyle | November 2025 | Data Analyst Position Interview

Web Application Link: https://brhoyle-nashville-predators-project.streamlit.app/  
GitHub Repo: https://github.com/br-hoyle/nashville-predators-project  

## Assignment
Our assistant coach is responsible for determining which players should take faceoffs in different situations. To support his decisions, he’s asked for deeper insights from our team’s faceoff data. For this first stage in evaluating your skills as a data analyst, we’d like you to show how you would approach this project using the sample data provided.

## Overview
The completed project has three main sections:
1. Team Level Analysis: Analyzing overall team faceoff win percentages across different zones, periods, and situations.
2. Player Level Analysis: Evaluating individual player performance in faceoffs, including win percentages in various zones and situations.
3. Faceoff Recommender: Predicting the winner of a faceoff based on game context, such as score differential, zone, and strength situations.

## Team Level Analysis
This section provides aggregate win rates for the team under varying circumstances. The chart provides the locations on the ice where the team performs well - and not so well, and the table below in the expander labeled “Summary Table by Selected Dimensions” allows the user to calculate team aggregates at their desired dimension (e.g. zone, opponent, period, strength). This tooling would allow the coaches to identify areas of improvement for the team in general - with the goal of creating practice situations the entire team would benefit.

## Player Level Analysis
Similar to the ‘Team Level Analysis’ this section provides individual player performance in different faceoff situations. It allows for the user to select a player to visualize how they perform on the ice, and their win rates under varying circumstances. Individual player statistics provides coaching with the insights to create player-level improvement plans so that individual players have coaching custom tailored to their areas for improvement. 

## Faceoff Recommender
The final section of the project is a recommendation engine for who should take a faceoff in different situations. This task is completed using a RandomForest classifier trained on players historical performance, and then used to make predictions on the player(s) with the highest chance to win, given a user defined situation. It is assumed that the opponent in the faceoff is not known at the time when the recommendation is made - therefore, only the opposing teams aggregate win rate is included in the model.

The model is fit using as few inputs as necessary to maximize the models AUC. The selected inputs include:
- Is the chosen team (NSH) the home team?
- Who is the game against?
- How many more or less players does the chosen team have on the ice?
- How many seconds have elapsed in the game?
- Is the faceoff in the offensive, defensive, or neutral zone?
- How many points does the chosen team have?
- What is the point differential to the opposing team?

Some simple model evaluation metrics are provided for the fit model, including standard classification metrics - as well as charts for a confusion matrix, calibration curve, and AUC curve. While the solution provided is a lightly trained, and simple model, it provides the following scores: {AUC: 55.2%, Accuracy: 54.1%, F1 Score: 59.3%, Precision: 54.4%, Recall: 65.2%}.

While these metrics are not particularly strong - typically, an AUC above 70% would be ideal in most applications - they do provide the coaches with a strategy to perform better than guessing at random. Under their historical performance, they have won ~51% of faceoffs; if they utilize the provided model they could expect to win ~54% of faceoffs. While that would only be an additional 3 faceoffs wins per 100, across an entire game or season this difference could become highly impactful.

## Areas for Continuous Improvement
If provided more time, or given greater direction from the coaching staff, the following are areas where this project could be improved:
- Provide a better way to compare individual players within a team
- Provide trended metrics across a game, season or seasons.
- Compare performance to other teams in different situations.
- Improve the feature engineering, model tuning, or model selection for the recommendation engine (ex. player minutes, opponent minutes, playing with injury, player performance in game, player accolades, points/assists, etc)
- Compare all NHL players to identify potential trade opportunities
- Improve charting of key performance indicators to allow for digesting greater information in a single view, while also putting player performance into context
