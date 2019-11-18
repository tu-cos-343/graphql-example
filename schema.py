import psycopg2
# Import a bunch of content from the Graphene library. These imports allow us
# to implement the GraphQL schema.
from graphene import ObjectType, String, Schema, Int, Float, List, Field, DateTime, Mutation, InputObjectType
from psycopg2.extras import RealDictCursor

# Create a connection to Postgres. You will have to update the configuration information here.
db_connection = psycopg2.connect(
    dbname="dvdrental",
    user="tom",
    # password="<your password>",
    host="localhost"
)

# All the activity with the database will use this cursor object. The default cursor
# returns a Python tuple for each row in a result set. We make use of a dictionary-based
# alternative called `RealDictCursor`. It returns a bona fide Python dictionary containing
# the data from each row of any result set.
db_cursor = db_connection.cursor(
    cursor_factory=RealDictCursor
)


# A class that implements a GraphQL type for actors.
class Actor(ObjectType):
    class Meta:
        # This will show up as a description of this type in the GraphQL interface.
        # You can also provide a comment string for the class, which does the same.
        description = "Details for one actor"

    # These are the fields for the Actor type. Each is defined as a class variable,
    # allowing the ObjectType superclass to create behind-the-scenes functionality
    # to implement the proper GraphQL behavior.
    actor_id = Int(required=True)
    first_name = String(required=True)
    last_name = String(required=True)
    last_update = DateTime(required=True)


# GraphQL type for categories.
# Note that there are no custom resolvers; Graphene's default resolver does all the work here.
class Category(ObjectType):
    """Category for a film"""
    category_id = Int(required=True)
    name = String(required=True)
    last_update = DateTime(required=True)


# GraphQL type for films.
class Film(ObjectType):
    class Meta:
        description = "Details of one film"

    # These fields are all resolved by the Graphene default resolver.
    film_id = Int(required=True)
    title = String(required=True)
    description = String()
    release_year = Int()
    rental_duration = Int(required=True)
    rental_rate = Float(required=True)
    length = Int()
    replacement_cost = Float(required=True)
    last_update = DateTime(required=True)
    rating = String()

    # Because these are lists of other types, the default resolver won't be sufficient.
    actors = List(Actor)
    categories = List(Category)

    # Resolve the `actors` field. Note that the name of this function must match
    # the name of the field it resolves.
    # The first argument to this method, `film`, is the "parent" film object.
    # (You can see where it gets created in the `resolve_film` method of the `Query` class.
    #
    # What we're trying to do here is get all the actors for a particular film.
    # To resolve these actors, we create and execute a SQL query. The query joins
    # the `film_actor` and `actor` tables and retrieves the (single) row of this
    # join that contains the `film_id` of the film we're resolving. Note the use of
    # standard Psycopg2 query parameters to avoid SQL injection issues.
    #
    # The `fetchall` method retrieves a list of dictionaries, one for each actor in the result set.
    # This is the result of having configured our `db_cusor` to use `RealDictCursor`.
    # Happily, Graphene's default resolver knows how to match up the keys of a dictionary
    # with the fields of a type, so all the Actor fields will be resolved automatically.
    def resolve_actors(film, info):
        db_cursor.execute(
            """
            SELECT actor.actor_id, first_name, last_name, actor.last_update FROM actor
            INNER JOIN film_actor 
              ON actor.actor_id = film_actor.actor_id
            WHERE film_actor.film_id = %(film_pk)s 
            """,
            {"film_pk": film['film_id']}
        )
        return [Actor(**row_data) for row_data in db_cursor.fetchall()]

    # Retrieve the categories for this film. Refer to the documentation for `resolve_actors`,
    # which is analogous.
    def resolve_categories(film, info):
        db_cursor.execute(
            """
            SELECT category.category_id, name FROM category
            INNER JOIN film_category
                ON category.category_id = film_category.category_id
            WHERE film_category.film_id = %(film_pk)s 
            """,
            {"film_pk": film['film_id']}
        )
        return [Category(**row_data) for row_data in db_cursor.fetchall()]


# This is our top-level query type. All queries known to our GraphQL schema are declared here.
class Query(ObjectType):
    # A field that retrieves a single actor's data. The `actor_id` keyword argument
    # is used by `resolve_actor` to fetch a particular actor of interest.
    # Consistent with the definition of the `Actor` object, we define this keyword
    # to be an `Int` and mark it as required. (If it was absent, we wouldn't know
    # which actor to retrieve!)
    actor = Field(Actor, actor_id=Int(required=True))

    # A field that retrieves all actors from the database. Note that there is no keyword
    # argument here (we're getting them all) and that we're declaring a `List` of `Actor`s.
    actors = List(Actor, description="All the actors")

    categories = List(Category)
    film = Field(Film, film_id=Int(required=True))
    films = List(Film, description="All the films")

    # Resolve a single actor. Because the `actor` field is declared to receive the `actor_id`
    # argument, the resolver expects to receive it. We construct the query for just this actor,
    # fetch it from the database, and return the resulting dictionary, which the Graphene default
    # resolver picks through to create the `Actor` object itself.
    def resolve_actor(root, info, actor_id):
        db_cursor.execute(
            """
            SELECT * FROM actor
            WHERE actor_id = %(id)s
            """,
            {'id': actor_id}
        )
        return Actor(**db_cursor.fetchone())

    # Resolve the list of all actors.
    def resolve_actors(root, info):
        db_cursor.execute("SELECT * FROM actor")
        return db_cursor.fetchall()

    def resolve_categories(root, info):
        db_cursor.execute("SELECT * FROM category")
        return db_cursor.fetchall()

    def resolve_film(root, info, film_id):
        db_cursor.execute(
            """
            SELECT * FROM film
            WHERE film_id = %(film_id)s
            """,
            {'film_id': film_id}
        )
        result = db_cursor.fetchone()
        return result

    def resolve_films(root, info):
        db_cursor.execute("SELECT * FROM film")
        return db_cursor.fetchall()


# This class defines a mutation that will create a new film category.
class CreateCategory(Mutation):
    """Create a new film category."""

    # Because we need to supply the name of a new category, we declar this
    # metaclass that tells the mutation to require a single string argument.
    class Arguments:
        name = String(required=True)

    # Like fields in the query classes, we also define the "shape" of the value that will be
    # returned by this mutation. For the client's convenience, we'll construct a type that
    # reflects all the columns in the underlying table.
    #
    # The `name` is the only field we have to supply. The others are created by the database
    # when we insert a new category: `category_id` is a synthetics key and `last_update` is
    # defined to default to the current time.
    category_id = Int(required=True)
    name = String(required=True)
    last_update = DateTime(required=True)

    # A mutation must define a method called `mutate`. The `name` argument reflects
    # the field found in the `Arguments` subclass, above.
    def mutate(root, info, name):
        db_cursor.execute(
            """
            INSERT INTO category(name)
            VALUES (%(name)s)
            RETURNING *
            """,
            {"name": name}
        )
        # The INSERT statement is simple, but includes a Postgres-specific wrinkle.
        # What we want to do in this mutation is return a category object
        # to the client. Most database servers would require us to INSERT the new category
        # data, then issue a second query to fetch it in order to access the automatically
        # generated column values (`category_id` and `last_update`). Postgres extends SQL
        # with the RETURNING clause. It lets us to return a one-row result set that includes
        # any (or, here, all) columns of the newly inserted row. No second query required!
        new_category = db_cursor.fetchone()
        db_connection.commit()
        # We want to return back a `CreateCategory` object. It's constructor needs to have
        # values for each of the fields defined above. Rather than listing them individually,
        # we'll pass them with the ** argument syntax, which "expands" all the dictionary's
        # attributes into individual arguments.
        return CreateCategory(**new_category)


# Another mutation for categories, this time, deleting an exisiting category.
class DeleteCategory(Mutation):
    """Delete a film category."""

    class Arguments:
        category_id = Int(required=True)

    # We're going to return an object containing the number of rows deleted.
    rows_affected = Int(required=True)

    def mutate(root, info, category_id):
        db_cursor.execute(
            """
            DELETE FROM category
            WHERE category_id=%(cat_pk)s
            """,
            {"cat_pk": category_id}
        )
        # The `rowcount` is a standard attribute of the Psycopg2 cursor object.
        # We use it to construct the object returned to the client.
        row_count = db_cursor.rowcount
        db_connection.commit()
        return DeleteCategory(rows_affected=row_count)


# This class defines a GraphQL input type. Although this example has only two fields,
# defining an input type for complex inputs is a best practice. See the CreateActor
# mutation for how this object is used.
class ActorInput(InputObjectType):
    first_name = String(required=True)
    last_name = String(required=True)


class CreateActor(Mutation):
    """Create an actor."""

    class Arguments:
        actor_input = ActorInput(required=True)

    class Meta:
        # We're going to return not a `CreateActor`, but an `Actor`
        output = Actor

    def mutate(root, info, actor_input):
        db_cursor.execute(
            """
            INSERT INTO actor(first_name, last_name)
            VALUES (%(first)s, %(last)s)
            RETURNING *
            """,
            {
                "first": actor_input.first_name,
                "last": actor_input.last_name
            })
        new_actor = db_cursor.fetchone()
        db_connection.commit()
        return Actor(**new_actor)


# Analogous to the Query object, this object collects all the GraphQL mutations.
class Mutation(ObjectType):
    create_category = CreateCategory.Field()
    delete_category = DeleteCategory.Field()
    create_actor = CreateActor.Field()


# The top-level object for the GraphQL schema, this class constructor takes
# the query and mutation objects created above. Our Flask server (`app.py`)
# imports this object in order to serve GraphQL requests defined here.
schema = Schema(
    query=Query,
    mutation=Mutation
)
