from typing import Annotated

from fastapi import Depends

from .service import CityService

CityServiceDep = Annotated[CityService, Depends(CityService)]
