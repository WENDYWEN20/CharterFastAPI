from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapp.schemas import PostCreate, PostResponse
from fastapp.db import create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield
    
app=FastAPI(lifespan=lifespan)
@app.post("/upload")
async def upload_file(
        file: UploadFile = File(...), 
        caption: str = Form(""), 
        session: AsyncSession = Depends(get_async_session)
):
    post = Post(
        caption=caption,
        url='dummyurl',
        file_type='photo',
        file_name='dummy name',
        )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post
@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()).limit(10))
    posts = [row[0] for row in result.all()]
    posts_data = []
    for post in posts:
        posts_data.append({
            "id": str(post.id),
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat(),
        })
    return {"posts": posts_data} 


# @app.get("/")
# def read_root():
#     return {"message": "World"}

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