from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapp.db import Post, User, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from fastapp.images import imagekit
import os
import uuid
import shutil
import tempfile
from fastapp.users import auth_backend, current_active_user, fastapi_users
from fastapp.schemas import UserRead, UserUpdate, UserCreate, PostCreate, PostResponse
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield
app=FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend),prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth",tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])
@app.post("/upload")

async def upload_file(
        file: UploadFile = File(...), 
        caption: str = Form(""), 
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session)
):
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
            
        upload_result = imagekit.files.upload(
            file=open(temp_file_path, 'rb'),
            file_name=file.filename,
            use_unique_file_name=True,
            tags=["backend-upload"],
        )
        
        if upload_result.response_metadata.http_status_code ==200:
            post = Post(
                user_id = user.id,
                caption=caption,
                url=upload_result.url,
                file_type='photo',
                file_name=file.filename,
                )
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()
        
@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()).limit(10))
    posts = [row[0] for row in result.all()]
    result = await session.execute(select(User))
    user_dict = {u.id: u.email for u in users}
    posts_data = []
    for post in posts:
        posts_data.append({
            "id": str(post.id),
            "user_id": str(post.user_id),
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat(),
            "is_owner": post.user_id == user.id,
            "email": user_dict.get(post.user_id, "Unknown") 
        })
    return {"posts": posts_data} 

@app.delete("/posts/{post_id}")
async def delete_post(post_id:str, session:AsyncSession=Depends(get_async_session), user: User = Depends(current_active_user)):
    try:
        post_uuid = uuid.UUID(post_id)
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        await session.delete(post)
        await session.commit()
        return {"message": "Post deleted successfully"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid post ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "World"}

# text_posts = {
#     1: {"title": "Welcome to FastAPI", "content": "FastAPI is a modern, fast web framework for building APIs with Python 3.6+ based on standard Python type hints."},
#     2: {"title": "Getting Started with Python", "content": "Python is a versatile programming language that's perfect for beginners and professionals alike. Start your journey today!"},
#     3: {"title": "Web Development Tips", "content": "Always validate your inputs, use proper error handling, and keep your code clean and readable for better maintenance."},
#     4: {"title": "Database Best Practices", "content": "Use connection pooling, implement proper indexing, and always sanitize user inputs to prevent SQL injection attacks."},
#     5: {"title": "API Design Guidelines", "content": "Follow RESTful principles, use appropriate HTTP status codes, and provide clear documentation for your API endpoints."},
#     6: {"title": "Testing Your Code", "content": "Write unit tests, integration tests, and end-to-end tests to ensure your application works as expected and remains reliable."},
#     7: {"title": "Performance Optimization", "content": "Profile your code to identify bottlenecks, use caching strategies, and optimize database queries for better performance."},
#     8: {"title": "Security Considerations", "content": "Implement proper authentication, use HTTPS, validate all inputs, and keep your dependencies updated to maintain security."},
#     9: {"title": "Deployment Strategies", "content": "Use containerization with Docker, implement CI/CD pipelines, and monitor your applications in production environments."},
#     10: {"title": "Learning Resources", "content": "Read documentation, follow tutorials, join communities, and practice coding regularly to improve your programming skills."}
# }
# @app.get("/posts")
# def get_all_posts(limit: int=None):
#     if limit:
#         return list(text_posts.values())[:limit]
#     return text_posts
# @app.get("/posts/{post_id}")
# def get_post(id:int):
#     if id not in text_posts:
#         raise HTTPException(status_code=404, detail="Post not found")
#     return text_posts[id]
# @app.post('/posts')
# def create_post(post: PostCreate)->PostResponse:
#     new_post= {"title": post.title, "content": post.content}
#     text_posts[max(text_posts.keys())+1]= new_post
#     return new_post
