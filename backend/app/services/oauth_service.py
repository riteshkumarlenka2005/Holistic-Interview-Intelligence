"""
OAuth service for Google and GitHub authentication
"""
import httpx
from urllib.parse import urlencode
from typing import Optional
import logging

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class GoogleOAuth:
    """Google OAuth 2.0 handler"""
    
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    @staticmethod
    def get_auth_url(state: str = None) -> str:
        """Generate Google OAuth consent URL"""
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        if state:
            params["state"] = state
        
        return f"{GoogleOAuth.AUTH_URL}?{urlencode(params)}"
    
    @staticmethod
    async def exchange_code(code: str) -> Optional[dict]:
        """
        Exchange authorization code for user info
        Returns: {email, name, picture, oauth_id} or None
        """
        try:
            async with httpx.AsyncClient() as client:
                # Exchange code for tokens
                token_response = await client.post(
                    GoogleOAuth.TOKEN_URL,
                    data={
                        "client_id": settings.google_client_id,
                        "client_secret": settings.google_client_secret,
                        "code": code,
                        "redirect_uri": settings.google_redirect_uri,
                        "grant_type": "authorization_code",
                    }
                )
                
                if token_response.status_code != 200:
                    logger.error(f"Google token exchange failed: {token_response.text}")
                    return None
                
                tokens = token_response.json()
                access_token = tokens.get("access_token")
                
                if not access_token:
                    logger.error("No access token in Google response")
                    return None
                
                # Get user info
                userinfo_response = await client.get(
                    GoogleOAuth.USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if userinfo_response.status_code != 200:
                    logger.error(f"Google userinfo failed: {userinfo_response.text}")
                    return None
                
                userinfo = userinfo_response.json()
                
                return {
                    "email": userinfo.get("email"),
                    "name": userinfo.get("name", ""),
                    "first_name": userinfo.get("given_name", ""),
                    "last_name": userinfo.get("family_name", ""),
                    "picture": userinfo.get("picture"),
                    "oauth_id": userinfo.get("id"),
                }
                
        except Exception as e:
            logger.error(f"Google OAuth error: {str(e)}")
            return None


class GitHubOAuth:
    """GitHub OAuth handler"""
    
    AUTH_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USERINFO_URL = "https://api.github.com/user"
    EMAILS_URL = "https://api.github.com/user/emails"
    
    @staticmethod
    def get_auth_url(state: str = None) -> str:
        """Generate GitHub OAuth consent URL"""
        params = {
            "client_id": settings.github_client_id,
            "redirect_uri": settings.github_redirect_uri,
            "scope": "user:email read:user",
        }
        if state:
            params["state"] = state
        
        return f"{GitHubOAuth.AUTH_URL}?{urlencode(params)}"
    
    @staticmethod
    async def exchange_code(code: str) -> Optional[dict]:
        """
        Exchange authorization code for user info
        Returns: {email, name, picture, oauth_id} or None
        """
        try:
            async with httpx.AsyncClient() as client:
                # Exchange code for token
                token_response = await client.post(
                    GitHubOAuth.TOKEN_URL,
                    data={
                        "client_id": settings.github_client_id,
                        "client_secret": settings.github_client_secret,
                        "code": code,
                        "redirect_uri": settings.github_redirect_uri,
                    },
                    headers={"Accept": "application/json"}
                )
                
                if token_response.status_code != 200:
                    logger.error(f"GitHub token exchange failed: {token_response.text}")
                    return None
                
                tokens = token_response.json()
                access_token = tokens.get("access_token")
                
                if not access_token:
                    logger.error(f"No access token in GitHub response: {tokens}")
                    return None
                
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                # Get user info
                userinfo_response = await client.get(
                    GitHubOAuth.USERINFO_URL,
                    headers=headers
                )
                
                if userinfo_response.status_code != 200:
                    logger.error(f"GitHub userinfo failed: {userinfo_response.text}")
                    return None
                
                userinfo = userinfo_response.json()
                
                # Get primary email (might be private)
                email = userinfo.get("email")
                if not email:
                    emails_response = await client.get(
                        GitHubOAuth.EMAILS_URL,
                        headers=headers
                    )
                    if emails_response.status_code == 200:
                        emails = emails_response.json()
                        primary_email = next(
                            (e["email"] for e in emails if e.get("primary") and e.get("verified")),
                            None
                        )
                        email = primary_email or (emails[0]["email"] if emails else None)
                
                # Parse name
                full_name = userinfo.get("name", "") or ""
                name_parts = full_name.split(" ", 1)
                first_name = name_parts[0] if name_parts else ""
                last_name = name_parts[1] if len(name_parts) > 1 else ""
                
                return {
                    "email": email,
                    "name": full_name,
                    "first_name": first_name,
                    "last_name": last_name,
                    "picture": userinfo.get("avatar_url"),
                    "oauth_id": str(userinfo.get("id")),
                    "username": userinfo.get("login"),
                }
                
        except Exception as e:
            logger.error(f"GitHub OAuth error: {str(e)}")
            return None
