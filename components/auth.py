"""
Authentication components for Vizion.
Handles Google OAuth, email/password login, and registration.
"""

import streamlit as st
import bcrypt
import uuid
from datetime import datetime
from google.oauth2 import id_token
from google.auth.transport import requests
import json


def get_google_oauth_url(client_id, redirect_uri):
    """Generate Google OAuth URL."""
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    scope = "openid email profile"
    
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
        "access_type": "offline",
        "prompt": "consent"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{query_string}"


def verify_google_token(token, client_id):
    """Verify Google ID token and return user info."""
    try:
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            client_id
        )
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        return {
            'oauth_id': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo.get('name', ''),
            'profile_picture': idinfo.get('picture', ''),
            'email_verified': idinfo.get('email_verified', False)
        }
    except Exception as e:
        st.error(f"Token verification failed: {str(e)}")
        return None


def render_google_signin_button(client_id, redirect_uri):
    """Render a styled Google Sign-In button."""
    oauth_url = get_google_oauth_url(client_id, redirect_uri)
    
    st.markdown(
        f"""
        <a href="{oauth_url}" target="_self" style="text-decoration: none;">
            <div style="
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: white;
                color: #3c4043;
                border: 1px solid #dadce0;
                border-radius: 4px;
                padding: 10px 20px;
                font-family: 'Google Sans', Roboto, arial, sans-serif;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: background-color 0.2s, box-shadow 0.2s;
                margin: 10px 0;
            " onmouseover="this.style.backgroundColor='#f8f9fa'; this.style.boxShadow='0 1px 3px rgba(0,0,0,0.12)'" 
               onmouseout="this.style.backgroundColor='white'; this.style.boxShadow='none'">
                <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" 
                     alt="Google logo" 
                     style="width: 18px; height: 18px; margin-right: 10px;">
                Sign in with Google
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )


def handle_oauth_callback(session, User):
    """Handle OAuth callback and create/login user."""
    params = st.query_params
    
    # Check for OAuth code in URL
    if "code" in params:
        code = params["code"]
        if isinstance(code, list):
            code = code[0]
        
        # In production, exchange code for token here
        # For now, we'll use a simplified flow
        st.info("OAuth code received. In production, this would exchange for user info.")
        return None
    
    # Check for stored OAuth info (simplified flow)
    if "oauth_info" in st.session_state:
        oauth_info = st.session_state.oauth_info
        
        # Check if user exists
        user = session.query(User).filter_by(email=oauth_info['email']).first()
        
        if user:
            # Update OAuth info
            user.oauth_provider = 'google'
            user.oauth_id = oauth_info['oauth_id']
            user.profile_picture = oauth_info.get('profile_picture')
        else:
            # Create new user
            user = User(
                id=str(uuid.uuid4()),
                name=oauth_info['name'],
                email=oauth_info['email'],
                password_hash=None,  # No password for OAuth users
                oauth_provider='google',
                oauth_id=oauth_info['oauth_id'],
                profile_picture=oauth_info.get('profile_picture'),
                email_notifications='true'
            )
            session.add(user)
        
        session.commit()
        
        # Clear OAuth info from session state
        del st.session_state.oauth_info
        
        return user
    
    return None


def render_email_password_register(session, User):
    """Render email/password registration form."""
    st.subheader("Create your New Account")
    name = st.text_input("Full Name", key="reg_name")
    email = st.text_input("Email", key="reg_email")
    pwd = st.text_input("Password", type="password", key="reg_pwd")
    pwd_confirm = st.text_input("Confirm Password", type="password", key="reg_pwd_confirm")
    
    # Email notification preference
    email_notifs = st.checkbox("Send me email notifications about my analyses", value=True)

    if st.button("Register", key="reg_button"):
        if not name or not email or not pwd:
            st.error("Please fill all fields.")
        elif pwd != pwd_confirm:
            st.error("Passwords do not match.")
        elif len(pwd) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            existing_user = session.query(User).filter_by(email=email).first()
            if existing_user:
                st.error("User with this email already exists.")
            else:
                hashed_pwd = bcrypt.hashpw(
                    pwd.encode("utf-8"),
                    bcrypt.gensalt()
                ).decode("utf-8")
                new_user = User(
                    id=str(uuid.uuid4()),
                    name=name,
                    email=email,
                    password_hash=hashed_pwd,
                    oauth_provider='email',
                    email_notifications='true' if email_notifs else 'false'
                )
                session.add(new_user)
                session.commit()
                st.success("Account created! You can now log in.")
                return new_user
    
    return None


def render_email_password_login(session, User):
    """Render email/password login form."""
    st.subheader("Log in to your Account")
    email_login = st.text_input("Email", key="login_email")
    pwd_login = st.text_input("Password", type="password", key="login_pwd")

    if st.button("Login", key="login_button"):
        user = session.query(User).filter_by(email=email_login).first()
        
        if not user:
            st.error("No account found with this email.")
            return None
        
        # Check if OAuth user trying to login with password
        if user.oauth_provider and user.oauth_provider != 'email' and not user.password_hash:
            st.error(f"This account uses {user.oauth_provider.title()} sign-in. Please use the '{user.oauth_provider.title()} Sign In' button.")
            return None
        
        # Verify password
        if user.password_hash and bcrypt.checkpw(
            pwd_login.encode("utf-8"),
            user.password_hash.encode("utf-8")
        ):
            return user
        else:
            st.error("Invalid password.")
            return None
    
    return None


def render_auth_sidebar(session, User):
    """
    Render the complete authentication sidebar.
    Returns authenticated user or None.
    """
    st.sidebar.header("Login or Register")
    
    # Check for OAuth callback
    oauth_user = handle_oauth_callback(session, User)
    if oauth_user:
        return oauth_user
    
    # Check if already logged in
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "email" not in st.session_state:
        st.session_state.email = None
    
    # Check URL params for uid
    params = st.query_params
    if "uid" in params and st.session_state.get("user_id") is None:
        uid = params["uid"]
        if isinstance(uid, list):
            uid = uid[0]
        user = session.query(User).filter_by(id=uid).first()
        if user:
            st.session_state.user_id = user.id
            st.session_state.email = user.email
            return user
    
    if st.session_state.user_id is None:
        # Show login/register tabs
        tab_login, tab_register = st.sidebar.tabs(["Login", "Register"])
        
        with tab_login:
            # Google Sign-In button
            st.markdown("### Quick Sign In")
            
            # Get Google OAuth config from secrets
            try:
                if "google_oauth" in st.secrets:
                    client_id = st.secrets["google_oauth"]["client_id"]
                    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
                    render_google_signin_button(client_id, redirect_uri)
                else:
                    st.info("💡 Google Sign-In: Configure `google_oauth` in Streamlit secrets")
            except Exception as e:
                st.info("💡 Google Sign-In: Add credentials in Settings → Secrets")
            
            st.markdown("---")
            st.markdown("### Or use Email/Password")
            
            # Email/password login
            user = render_email_password_login(session, User)
            if user:
                st.session_state.user_id = user.id
                st.session_state.email = user.email
                st.query_params["uid"] = user.id
                st.success(f"Welcome back, {user.name}!")
                st.rerun()
        
        with tab_register:
            # Google Sign-In button
            st.markdown("### Quick Sign Up")
            
            try:
                if "google_oauth" in st.secrets:
                    client_id = st.secrets["google_oauth"]["client_id"]
                    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
                    render_google_signin_button(client_id, redirect_uri)
                else:
                    st.info("💡 Google Sign-In: Configure `google_oauth` in Streamlit secrets")
            except Exception as e:
                st.info("💡 Google Sign-In: Add credentials in Settings → Secrets")
            
            st.markdown("---")
            st.markdown("### Or use Email/Password")
            
            # Email/password registration
            user = render_email_password_register(session, User)
            if user:
                st.session_state.user_id = user.id
                st.session_state.email = user.email
                st.query_params["uid"] = user.id
                st.success(f"Welcome, {user.name}!")
                st.rerun()
        
        return None
    
    else:
        # User is logged in
        user = session.query(User).filter_by(id=st.session_state.user_id).first()
        if not user:
            # User deleted, logout
            st.session_state.user_id = None
            st.session_state.email = None
            st.query_params.clear()
            st.rerun()
            return None
        
        # Show user profile
        st.sidebar.markdown("---")
        
        if user.profile_picture:
            st.sidebar.image(user.profile_picture, width=80)
        
        st.sidebar.write(f"**{user.name}**")
        st.sidebar.write(f"📧 {user.email}")
        
        if user.oauth_provider and user.oauth_provider != 'email':
            st.sidebar.caption(f"Signed in with {user.oauth_provider.title()}")
        
        # Notification settings
        with st.sidebar.expander("⚙️ Notification Settings"):
            current_pref = user.email_notifications == 'true'
            new_pref = st.checkbox(
                "Email notifications", 
                value=current_pref,
                key="email_notif_toggle"
            )
            
            if new_pref != current_pref:
                user.email_notifications = 'true' if new_pref else 'false'
                session.commit()
                st.success("Settings updated!")
        
        if st.sidebar.button("Logout", key="logout_button"):
            st.session_state.user_id = None
            st.session_state.email = None
            st.query_params.clear()
            st.rerun()
        
        return user
