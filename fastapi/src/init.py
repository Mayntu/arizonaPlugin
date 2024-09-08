from fastapi import FastAPI
from src.database.settings import database, check_connection
from src.database.redis_client import redis_client
# import yaml

from fastapi.middleware.cors import CORSMiddleware


async def create_app() -> FastAPI:
    app = FastAPI(docs_url="/")
        
    origins = [
        "http://localhost:5000",
        
    ]

    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  
        allow_credentials=True,
        allow_methods=["*"],  
        allow_headers=["*"],  
    )

    try:
        await check_connection()
        
        if "tokens" not in await database.list_collection_names():
            print("Collection 'tokens' does not exist. Creating...")
            tokens = database["tokens"]
            
            print("Collection 'tokens' created.")
        else:
            print("Collection 'tokens' already exists.")

    except Exception as e:
        print(f"Error initializing MongoDB: {e}")

    register_views(app=app)

    # def custom_openapi():
    #     if app.openapi_schema:
    #         return app.openapi_schema
        
    #     with open("docs.yaml", encoding="utf-8") as f:
    #         openapi_schema = yaml.safe_load(f)
    #         app.openapi_schema = openapi_schema
    #         return app.openapi_schema
        
    # app.openapi = custom_openapi

    @app.on_event("startup")
    async def startup_event():
        await redis_client.init()
        print("redis on")

    @app.on_event("shutdown")
    async def shutdown_event():
        await redis_client.close()
        print("redis off")
    
    return app

def register_views(app: FastAPI):
    from src.controllers.main_controller import api_router
    app.include_router(api_router)
