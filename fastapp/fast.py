from fastapi import FastAPI, HTTPException
app=FastAPI()
@app.get("/")
def read_root():
    return {"message": "World"}

text_posts = {
    1: {"title": "Welcome to FastAPI", "content": "FastAPI is a modern, fast web framework for building APIs with Python 3.6+ based on standard Python type hints."},
    2: {"title": "Getting Started with Python", "content": "Python is a versatile programming language that's perfect for beginners and professionals alike. Start your journey today!"},
    3: {"title": "Web Development Tips", "content": "Always validate your inputs, use proper error handling, and keep your code clean and readable for better maintenance."},
    4: {"title": "Database Best Practices", "content": "Use connection pooling, implement proper indexing, and always sanitize user inputs to prevent SQL injection attacks."},
    5: {"title": "API Design Guidelines", "content": "Follow RESTful principles, use appropriate HTTP status codes, and provide clear documentation for your API endpoints."},
    6: {"title": "Testing Your Code", "content": "Write unit tests, integration tests, and end-to-end tests to ensure your application works as expected and remains reliable."},
    7: {"title": "Performance Optimization", "content": "Profile your code to identify bottlenecks, use caching strategies, and optimize database queries for better performance."},
    8: {"title": "Security Considerations", "content": "Implement proper authentication, use HTTPS, validate all inputs, and keep your dependencies updated to maintain security."},
    9: {"title": "Deployment Strategies", "content": "Use containerization with Docker, implement CI/CD pipelines, and monitor your applications in production environments."},
    10: {"title": "Learning Resources", "content": "Read documentation, follow tutorials, join communities, and practice coding regularly to improve your programming skills."}
}
@app.get("/posts")
def get_all_posts(limit: int=None):
    return text_posts
@app.get("/posts/{post_id}")
def get_post(id:int):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found")
    return text_posts[id]