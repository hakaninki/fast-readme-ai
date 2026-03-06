"""Sample FastAPI application for testing purposes."""

from fastapi import FastAPI


app = FastAPI()


class UserService:
    """Handles user-related business logic."""

    def get_user(self, user_id: int) -> dict:
        """Retrieve a user by ID."""
        return {"id": user_id, "name": "Test User"}


def calculate_total(items: list) -> float:
    """Calculate the total price of a list of items."""
    return sum(item.get("price", 0) for item in items)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello World"}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get a user by ID."""
    service = UserService()
    return service.get_user(user_id)
