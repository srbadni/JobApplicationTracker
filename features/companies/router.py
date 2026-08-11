from fastapi import APIRouter

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.get("")
def get_companies() -> None:
    """Reserved endpoint for the existing companies feature."""
