from typing import Annotated

from fastapi import Depends

from .service import ProvinceService

ProvinceServiceDep = Annotated[ProvinceService, Depends(ProvinceService)]
