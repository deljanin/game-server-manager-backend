from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from asgiref.sync import sync_to_async

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        print("JWTAuthMiddleware loaded")
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.authentication import JWTAuthentication
        from django.contrib.auth.models import AnonymousUser
        from django.db import close_old_connections

        query_string = scope.get("query_string", b"").decode()
        print(f"JWTAuthMiddleware: query_string={query_string}")
        query_params = parse_qs(query_string)
        token_list = query_params.get("token")
        token = token_list[0] if token_list else None

        if token:
            try:
                validated_token = UntypedToken(token)
                # Use sync_to_async for the ORM call
                user = await sync_to_async(JWTAuthentication().get_user)(validated_token)
                scope["user"] = user
                print(f"JWTAuthMiddleware: user authenticated: {user}")
            except Exception as e:
                print(f"JWTAuthMiddleware: Invalid token: {e}")
                scope["user"] = AnonymousUser()
        else:
            print("JWTAuthMiddleware: No token found in query string.")
            scope["user"] = AnonymousUser()
        close_old_connections()
        return await super().__call__(scope, receive, send)