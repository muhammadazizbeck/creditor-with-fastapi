from fastapi import FastAPI
from auth_routes.auth_routes import auth_router
from monitoring_routes.monitoring_routes import monitoring_router
from settings_routes.settings_routes import settings_router
from debts_routes.debts_routes import debts_router
from schemas import Settings
from fastapi_jwt_auth import AuthJWT


app = FastAPI()
app.include_router(auth_router)
app.include_router(monitoring_router)
app.include_router(settings_router)
app.include_router(debts_router)

@AuthJWT.load_config
def get_config():
    return Settings()

@app.get('/')
async def homepage():
    response = {
        'username':'muhammadazizbeck',
        'email':'aa2004bek@gmail.com',
        'password':"Azizbek1410"
    }
    return response