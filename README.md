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
   ```bash
   % git clone https://github.com/tu-cos-343/graphql-example.git
   ```
1. Change directory to your shiny new clone.
   ```bash
   % cd graphql-example
   ```
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
http://localhost:5000/graphql.

## GraphQL Schema

The `schema.py` file
implements our GraphQL schema.
You will find extensive comments in that file
that explain the various pieces and parts.
Please take the time to read over the comments
so that you understand how it works.

## Sample Queries

Following are examples of queries and mutations
that the `schema.py` file implements.
Note that if you are connecting to a read-only
database account,
you will not be able to execute the mutations.

1. Retrieve all the films in the database.
   Note that we also ask for the actors,
   which causes the `resolve_actors` method to run.
    ```
    query AllFilms {
      films {
        filmId
        title
        description
        actors {
          fullName
        }
      }
    }
    ```
1. Retrieve a single actor. 
   Here the `actorId` is passed as a parameter.
   ```
   query OneActor($id: Int!) {
     actor(actorId: $id) {
       firstName
       lastName
       lastUpdate
     }
   }
   ```
   In `GraphiQL`, use the *Query Variables*
   window to supply a JSON object with the ID.
   For example:
   ```json
   { "id": 42 }
   ``` 

1. Add a new category.
   Passes the name for the category directly.
   Probably better to use a parameter
   as shown for `OneActor`.
    ```
    mutation AddCategory {
      createCategory(name: "Nerd Films") {
        categoryId
        name
      }
    }
    ```
1. Delete a category.
   Delete an existing category by its category ID.
   Note that the database will still enforce
   referential integrity if another database entity
   refers to the category being deleted.    
    ```
    mutation DeleteCategory($id: Int!) {
      deleteCategory(categoryId: $id) {
        rowsAffected
      }
    }
    ```
1. Create an actor.
    ```
    mutation NewActor($input: ActorInput!) {
      createActor(actorInput: $input) {
        actorId
        firstName
        lastName
      }
    }
    ```
   Pass the details in the *Query Variables* window
    ```
    {
      "input": {
        "firstName": "Fred",
        "lastName": "Ziffle"
      }
    }
    ```
