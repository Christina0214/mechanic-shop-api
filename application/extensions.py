from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]) #creating an instance of Limiter and applying a default rate limit to entire project
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'}) #adding the Flask-Caching instance

ma = Marshmallow()