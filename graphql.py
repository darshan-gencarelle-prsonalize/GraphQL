import strawberry
from pymongo import MongoClient

# Create a MongoDB client
client = MongoClient('mongodb://localhost:27017')
database = client['sample_database']
collection = database['sample_collection']


@strawberry.type
class User:
    name: str
    age: int


@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> list[User]:
        # Retrieve all 'user' documents from the MongoDB collection
        return [User(name=user['name'], age=user['age']) for user in collection.find()]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, name: str, age: int) -> User:
        # Create a new 'user' document in the MongoDB collection
        result = collection.insert_one({"name": name, "age": age})
        if result.acknowledged:
            return User(name=name, age=age)
        return None


schema = strawberry.Schema(query=Query, mutation=Mutation)


def initialize_db():
    # Function to add some initial data to our MongoDB collection.
    initial_data = [
        {"name": "John Doe", "age": 20},
        {"name": "Jane Doe", "age": 25},
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 35},
    ]
    collection.insert_many(initial_data)


def start_api():
    from strawberry.flask.views import GraphQLView as BaseGraphQLView
    from flask import request
    class GraphQLView(BaseGraphQLView):
        def get_context(self) -> Any:
            return {"request": request}

    from flask import Flask, Response
    app = Flask(__name__)
    app.add_url_rule("/graphql", view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))
    app.run(host='0.0.0.0', debug=True)


if __name__ == "__main__":
    initialize_db()  # Initialize the DB with some data
    start_api()
