from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from users.routes import router as users_router
from books.routes import router as books_router
from auth.routes import router as auth_router

app = FastAPI(title="Book Rental Management API", version="1.0.0")

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Book Rental Management API is running!"}

app.include_router(users_router, prefix="")
app.include_router(books_router, prefix="")
app.include_router(auth_router, prefix="")
