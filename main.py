from flask import Flask, request, jsonify
from db import db
from models import User
import os
import redis
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://appuser:apppass@postgres-users:5432/users"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

redis_host = os.getenv("REDIS_HOST", "localhost")
cache = redis.Redis(host=redis_host, port=6379, decode_responses=True)

CACHE_TTL = 60  # segundos
EVENTS_QUEUE = "events-queue"


def publish_event(event_type, description):
    event = {
        "type": event_type,
        "source": "user-service",
        "description": description
    }
    cache.rpush(EVENTS_QUEUE, json.dumps(event))


@app.route("/users", methods=["POST"])
def create_user():
    data = request.json

    user = User(
        name=data["name"],
        email=data["email"]
    )

    db.session.add(user)
    db.session.commit()

    cache.delete("users:all")
    publish_event("USER_CREATED", f"User {user.name} created with email {user.email}")

    return jsonify({
        "id": str(user.id),
        "name": user.name,
        "email": user.email
    }), 201

@app.route("/users/<uuid:user_id>", methods=["GET"])
def get_user(user_id):
    cache_key = f"user:{user_id}"
    cached = cache.get(cache_key)
    if cached:
        return jsonify(json.loads(cached)), 200

    user = User.query.get_or_404(user_id)
    data = {"id": str(user.id), "name": user.name, "email": user.email}
    cache.setex(cache_key, CACHE_TTL, json.dumps(data))

    return jsonify(data), 200

@app.route("/users/<uuid:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    cache.delete(f"user:{user_id}")
    cache.delete("users:all")
    publish_event("USER_DELETED", f"User {user_id} deleted")

    return "", 204

@app.route("/users", methods=["GET"])
def list_users():
    cached = cache.get("users:all")
    if cached:
        return jsonify(json.loads(cached)), 200

    users = User.query.all()
    data = [
        {"id": str(user.id), "name": user.name, "email": user.email}
        for user in users
    ]
    cache.setex("users:all", CACHE_TTL, json.dumps(data))

    return jsonify(data), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)