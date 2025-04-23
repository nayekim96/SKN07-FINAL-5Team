from typing import Union
from fastapi import APIRouter, FastAPI, status
from pydantic import BaseModel
from .db_util.db_utils import post_db_connect
from .routers.main_routers import api_router

app = FastAPI(
    title="SKAI Networks7 mock interview",
    version="0.1"
)

app.include_router(api_router)

class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"

@app.get("/")
def read_root():
    return {"Hello": "World123"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get('/get_user_info')
def get_user_info():
    connect = post_db_connect()
    result = connect.select_one("select * from user_info where user_id = 'interview'")
    connect.close()
    return {'user_info' : result}

@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")

# @app.post("/query", status_code=200)
# async def query(data:Model~~~):
#     retriever = get_retriever(retriever_type)
#     model = get_models(model_name)
#     chain = retriever | prompt | model | stroutputparser()
#     res = chain.invoke()
#     return 0