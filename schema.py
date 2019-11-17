import psycopg2
from graphene import ObjectType, String, Schema, Int, Float, List, Field, DateTime, Mutation
from psycopg2.extras import RealDictCursor

db_connection = psycopg2.connect(
    dbname="dvdrental",
    user="tom",
    # password="<your password>",
    host="localhost"
)
db_cursor = db_connection.cursor(
    cursor_factory=RealDictCursor
)


class Actor(ObjectType):
    class Meta:
        description = "Details for one actor"

    actor_id = Int(required=True)
    first_name = String(required=True)
    last_name = String(required=True)
    last_update = DateTime(required=True)
    full_name = String()

    def resolve_full_name(actor, info):
        return f"{actor['first_name']} {actor['last_name']}"


class Category(ObjectType):
    """Category for a film"""
    category_id = Int(required=True)
    name = String(required=True)
    last_update = DateTime()


class Film(ObjectType):
    class Meta:
        description = "Details of one film"

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

    actors = List(Actor)
    categories = List(Category)

    def resolve_actors(film, info):
        db_cursor.execute(
            """
            SELECT * FROM actor
            INNER JOIN film_actor 
              ON actor.actor_id = film_actor.actor_id
            WHERE film_actor.film_id = %(film_pk)s 
            """,
            {"film_pk": film['film_id']}
        )
        return db_cursor.fetchall()

    def resolve_categories(film, info):
        db_cursor.execute(
            """
            SELECT * FROM category
            INNER JOIN film_category
                ON category.category_id = film_category.category_id
            WHERE film_category.film_id = %(film_pk)s 
            """,
            {"film_pk": film['film_id']}
        )
        return db_cursor.fetchall()


class Query(ObjectType):
    actor = Field(Actor, actor_id=Int(required=True))
    actors = List(Actor, description="All the actors")
    categories = List(Category)
    film = Field(Film, film_id=Int(required=True))
    films = List(Film, description="All the films")

    def resolve_actor(root, info, actor_id):
        db_cursor.execute(
            """
            SELECT * FROM actor
            WHERE actor_id = %(id)s
            """,
            {'id': actor_id}
        )
        return db_cursor.fetchone()

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


class CreateCategory(Mutation):
    """Create a new film category."""

    class Arguments:
        name = String(required=True)

    category_id = Int(required=True)
    name = String(required=True)
    last_update = DateTime(required=True)

    def mutate(parent, info, name):
        db_cursor.execute(
            """
            INSERT INTO category(name)
            VALUES (%(name)s)
            RETURNING *
            """,
            {"name": name}
        )
        new_category = db_cursor.fetchone()
        db_connection.commit()
        return CreateCategory(**new_category)


class DeleteCategory(Mutation):
    """Delete a film category."""

    class Arguments:
        category_id = Int(required=True)

    rows_affected = Int(required=True)

    def mutate(parent, info, category_id):
        db_cursor.execute(
            """
            DELETE FROM category
            WHERE category_id=%(cat_pk)s
            """,
            {"cat_pk": category_id}
        )
        row_count = db_cursor.rowcount
        db_connection.commit()
        return DeleteCategory(rows_affected=row_count)


class Mutation(ObjectType):
    create_category = CreateCategory.Field()
    delete_category = DeleteCategory.Field()


schema = Schema(
    query=Query,
    mutation=Mutation
)
