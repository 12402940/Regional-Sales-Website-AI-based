import streamlit as st
# security/auth.py
import sqlite3
from passlib.hash import bcrypt  

DB = "users.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )""")
    conn.commit(); conn.close()

def add_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB); c = conn.cursor()
    try:
        pwd_hash = bcrypt.hash(password)
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pwd_hash))
        conn.commit(); return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username=?", (username,))
    row = c.fetchone(); conn.close()
    return bool(row and bcrypt.verify(password, row[0]))



init_db()

def show():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = ""
    if "page" not in st.session_state:
        st.session_state["page"] = "Login" 

    st.markdown("""
    <style>
        /* General App Styling */
        .stApp {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
        }

        /* Main container for the form */
        .form-container {
            padding: 2rem;
            border-radius: 20px;
            position: relative;
            overflow: hidden; /* Important for the animated border */
        }

        /* Animated Gradient Border */
        .form-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(
                transparent,
                rgba(0, 255, 204, 1),
                transparent 30%
            );
            animation: rotate 4s linear infinite;
        }

        @keyframes rotate {
            100% {
                transform: rotate(360deg);
            }
        }
        
    
        /* Welcome Image Animation */
        .welcome-image img {
            border-radius: 20px;
            animation: float 6s ease-in-out infinite;
            box-shadow: 0 0 20px rgba(0, 255, 204, 0.5);
        }

        /* Profile Picture Styling */
        .profile-pic {
            display: flex;
            justify-content: center;
            margin-bottom: 1.5rem;
        }
        .profile-pic img {
            border-radius: 50%;
            width: 100px;
            height: 100px;
            border: 4px solid #00ffcc;
            box-shadow: 0 0 25px rgba(0, 255, 204, 0.7);
        }

        /* Title Styling */
        .form-title {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            color: #ffffff;
            margin-bottom: 2rem;
        }
        
        /* --- NEW STYLES FOR SLEEKER INPUTS --- */
        div[data-testid="stTextInput"] > label {
            display: none; /* Hide label */
        }

        div[data-testid="stTextInput"] input {
            background-color: transparent;
            border: none;
            border-bottom: 2px solid #444; /* Underline effect */
            border-radius: 0; /* Remove rounded corners */
            color: white;
            outline: none;
            transition: border-bottom 0.3s ease-in-out;
            padding: 0.5rem 0; /* Adjust padding */
            margin-top: 1rem; /* Space them out */
        }

        div[data-testid="stTextInput"] input:focus {
            border-bottom-color: #00ffcc; /* Glow effect on focus */
            box-shadow: none;
        }
        /* --- END NEW STYLES --- */

        /* Streamlit Button overrides */
        .stButton > button {
            border-radius: 10px;
            background: linear-gradient(45deg, #00ffcc, #00b38f);
            color: #1a1a2e;
            font-weight: bold;
            border: none;
            transition: all 0.3s ease-in-out;
            margin-top: 2rem; /* Add space above button */
        }
        .stButton > button:hover {
            box-shadow: 0 0 20px rgba(0, 255, 204, 0.5);
            transform: scale(1.05);
        }

        /* Link to swap forms */
        .swap-link {
            text-align: center;
            margin-top: 1.5rem;
        }
        .swap-link button {
            background: none;
            border: none;
            color: #00ffcc;
            text-decoration: underline;
            cursor: pointer;
            font-size: 1rem;
        }
                

    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="
        text-align:center;
        padding: 1rem;
        font-size: 2.5rem;
        font-weight: bold;
        color: #00ffcc;
        text-shadow: 0 0 10px #00ffcc, 0 0 20px #00b38f;
        border-bottom: 2px solid rgba(0,255,204,0.3);
        margin-bottom: 2rem;
    ">
        🌐 Regional Sales Data Website
    </div>
    """, unsafe_allow_html=True)


    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown('<div class="welcome-image">', unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/8662/8662462.png", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<h1 style="text-align: center;">Welcome!</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center;">Log in to access your dashboard and manage your tasks.</p>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-inner-container">', unsafe_allow_html=True)

        if st.session_state["page"] == "Login":
            st.markdown('<div class="profile-pic"><img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png"></div>', unsafe_allow_html=True)
            st.markdown('<div class="form-title">Sign In</div>', unsafe_allow_html=True)
            
            username = st.text_input("Username", key="login_username", placeholder="Username", label_visibility="collapsed")
            password = st.text_input("Password", type="password", key="login_password", placeholder="Password", label_visibility="collapsed")

            if st.button("LOGIN", use_container_width=True):
                if verify_user(username, password):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.success(f"✅ Welcome!, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")
            
            st.markdown('<div class="swap-link">', unsafe_allow_html=True)
            if st.button("Don't have an account? Sign Up"):
                st.session_state["page"] = "Sign Up"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state["page"] == "Sign Up":
            st.markdown('<div class="profile-pic"><img src="https://cdn-icons-png.flaticon.com/512/9987/9987339.png"></div>', unsafe_allow_html=True)
            st.markdown('<div class="form-title">Create Account</div>', unsafe_allow_html=True)

            new_user = st.text_input("Choose Username", key="signup_username", placeholder="Choose Username", label_visibility="collapsed")
            new_pass = st.text_input("Choose Password", type="password", key="signup_password", placeholder="Choose Password", label_visibility="collapsed")

            if st.button("SIGN UP", use_container_width=True):
                if new_user and new_pass:
                    if add_user(new_user, new_pass):
                        st.success("🎉 Account created! You can now log in.")
                        st.session_state["page"] = "Login"
                        st.rerun()
                    else:
                        st.error("⚠️ This username is already taken. Please choose another.")
                else:
                    st.warning("Please fill in both fields.")
            
            st.markdown('<div class="swap-link">', unsafe_allow_html=True)
            if st.button("Already have an account? Login"):
                st.session_state["page"] = "Login"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)

