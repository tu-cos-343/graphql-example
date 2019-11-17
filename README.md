# Sample GraphQL Server

This simple server illustrates how to serve GraphQL requests.
It uses:
1. The [Graphene package for Python](https://graphene-python.org/)
1. The [psycopg2](http://initd.org/psycopg/) module to connect to Postgre
1. A [PostgreSQL](https://www.postgresql.org/) database
   set up with the DVD Rental example database.
1. A simple [Flask](https://flask.palletsprojects.com/en/) server
   to process requests from the GraphQL client
1. The [GraphiQL](https://github.com/graphql/graphiql) browser-based GraphQL client

## Installation

1. Clone the repository via Git.
1. Change directory to your shiny new clone.
1. Create a Python3 virtual environment.
   ```bash
   % python3 -m venv venv
   ```
1. Install the required Python packages.
   ```bash
   % pip install -r requirements.txt
   ```
1. Update the database connection parameters
   near the top of `schema.py`

## Flask Server

Find the Flask server in `app.py`.
It uses [flask-graphql](https://github.com/graphql-python/flask-graphql)
to interface with the Graphene package
using a specialized view function called `GraphQLView`.

Run the server from the command line:
```bash
% python app.py
```

By default,
the Flask configuration will listen on 
http://localhost:5000.
Because `app.py` enables GraphiQL support,
you can access the GraphiQL IDE in your browser
at 
http://localhost:5000/graphiql.




## GraphQL Schema