from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import HTTPException, status

rate_limit = defaultdict(list)

def check_rate_limit(user_id: str):
    now = datetime.now()
    window = 60   
    limit = 10  
    cutoff = now - timedelta(seconds=window)

    new_requests = []
    for t in rate_limit[user_id]:
        if t > cutoff:
            new_requests.append(t)
    rate_limit[user_id] = new_requests

    # Check if limit exceeded
    if len(rate_limit[user_id]) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Try again later."
        )

    # Add current request
    rate_limit[user_id].append(now)
    return True
