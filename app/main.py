from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.api.routes.campaigns import router as campaigns_router
from app.api.routes.offers import router as offers_router


app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
)

app.include_router(campaigns_router)
app.include_router(offers_router)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_name": settings.app_name},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
