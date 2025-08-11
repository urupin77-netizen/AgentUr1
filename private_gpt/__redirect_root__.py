from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/docs", status_code=302)
