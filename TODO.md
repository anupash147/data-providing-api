# Description

This project will initiate dataform in gcp platform. The dataform will create a cached view table which extract data in the increment of 10 rows every time it runs and populate the table. The api will furnish the data when called


# Tasks

[x] Create a gcp dataform with a table definition that will hold the results of the query `SELECT gender,state,year,name
    FROM `bigquery-public-data.usa_names.usa_1910_2013`
    LIMIT 5` Only year is integer rest all are String.

[x] Create a Make file that will check if dataform create in above task exists if not create it. Once done it will trigger to update the table.

[x] create a python api that will run in a docker container. This api will request the data from the table. It will take the column filter parameters and return the result as json.

[x] the api will need to have test cases.

[x] write a github workflow to implement cicd process of building the docker and push image to gcp repository. 