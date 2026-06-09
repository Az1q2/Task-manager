from fastapi import Cookie, HTTPException, status

def get_page_user_id(user_id: str | None = Cookie(None)) -> int:
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        return int(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)