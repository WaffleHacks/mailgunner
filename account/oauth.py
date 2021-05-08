from authlib.integrations.django_client import OAuth, DjangoRemoteApp
from typing import Dict


def normalize_userinfo(_client, data: Dict[str, str]) -> Dict[str, str]:
    return {
        "id": data["id"],
        "username": data["username"] + "#" + data["discriminator"],
        "email": data["email"],
    }


oauth = OAuth()
oauth.register(
    "discord",
    api_base_url="https://discord.com/api/",
    access_token_url="https://discord.com/api/oauth2/token",
    authorize_url="https://discord.com/api/oauth2/authorize",
    userinfo_endpoint="https://discord.com/api/users/%40me",
    userinfo_compliance_fix=normalize_userinfo,
    client_kwargs={
        "token_endpoint_auth_method": "client_secret_post",
        "scope": "identify email guilds",
    },
)


def get_discord_client() -> DjangoRemoteApp:
    """
    Get a Discord OAuth2 client
    """
    return oauth.create_client("discord")
