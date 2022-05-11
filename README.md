# US Congress Sentiment Analysis

A system to analyze the public sentiment of a bill, based upon tweets about that bill.

## Running

First, clone this repository. Additionally, this repository makes use of git-lfs for storage of the ML model. You must first install git-lfs, then perform

```bash
git-lfs pull
```

After cloning the repository.

Next, copy app/util/cred_example.json to create app/util/cred.json. Fill in the relevant values

Finally, run

```bash
docker-compose build
docker-compose up
```

And all containers will be spun up. Note that this application is intended to be run in docker, and is not intended to run without it.

## Important Files

### Building and Running

- Dockerfile: This contains the docker container definition
- docker-compose.yml: This orchestrates all of the necessary containers when the application is run locally. It should not be used in production
- ecs_json: This folder contains all of the json files to deploy this application to AWS ECS.
- .gitlab-ci.yml This contains the gitlab ci/cd pipeline code
- app/runner_example.py: This is a file which can import other files and be run from the commandline. All files must be run from this level, in order for imports to work properly.
- app/initializer.py: This is run by the initializer, and performs migrations.

### API Server

- app/server: This folder contains all the files to run the API server

### Celery Tasks

- app/tasks/task_initializer.py: This is the file run by (most) celery workers, telling it where to find the task definitions
- app/tasks/task_ml_initializer.py: This is the file run by the ml worker, since this worker specifically needs root access
- app/tasks/twitter_tasks.py: Defines each of the tasks for pulling twitter data, including tweets and users

### Dashboard

- app/dashboard/dashboard2.py: This is the file containing all the dashboard code. This is created using the Dash library

### APIs

- app/apis/twitter_api: Contains all the twitter API method calls, meant to serve as a convenience class

### Database

- app/db/models.py: Contains all the orm models using the SQL Alchemy library. This is arguably the most important file in this project (According to nick lol)
- app/db/database_connection.py: Run the initialize() function once at the start of a thread running, and run create_session() to create a SQLAlchemy session
- app/db/db_utils.py: Contains helper functions. The most useful here is the get_or_create() function, which allows for you to request the retrieval of a object, or if it does not exist, create it. This is meant to replicate Django's get_or_create() function.

### Machine Learning

- app/machine_learning/aggregation/aggregation_scaffold.py: Contains the code to run aggregations. Note that it pulls all tweets for a bill once, and passes these db objects around to conserve db calls
- app/machine_learning/keyword_extraction/get_keywords.py: This generates keywords for a bill
- app/machine_learning/sentiment_analysis/tweet_sentiment_analysis.py: Gets the sentiments of tweets in batches