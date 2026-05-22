"""
Permissions — 角色装饰器
"""

from fastapi import Depends, HTTPException
from backend.api.routes_auth import (
    get_current_user,
)


def require_role(role: str):
    """限制指定角色才能访问"""

    async def role_checker(
        current_user=Depends(get_current_user),
    ):
        if current_user.get("role") != role:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Forbidden: "
                    f"requires {role} role"
                ),
            )
        return current_user

    return role_checker
