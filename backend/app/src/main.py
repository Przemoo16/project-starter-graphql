from fastapi import FastAPI

app = FastAPI(
    title="project-starter-graphql",
    version="0.1.0",
    description="Project Starter GraphQL",
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
