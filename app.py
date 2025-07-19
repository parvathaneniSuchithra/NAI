import streamlit as st
import json
import pandas as pd
import os
import time

# --- Configuration ---
QUESTIONS_FILE = "questions_sample.json"
USERS_FILE = "users.json"
USER_PROGRESS_FILE = "user_progress.json"

# --- Custom CSS for a Clean, Modern, and Professional Professional Look with Theme Support ---
def apply_custom_css(theme):
    # Define CSS variables for both light and dark themes
    # These variables will be used throughout the CSS for consistent styling
    light_theme_vars = """
        --primary-color: #4A90E2; /* A softer, more professional blue */
        --secondary-color: #6C757D; /* Muted grey for secondary elements */
        --background-color: #F8F9FA; /* Very light grey for main background */
        --card-background: #FFFFFF; /* Pure white for cards/containers */
        --text-color: #343A40; /* Dark charcoal for primary text */
        --accent-light: #EBF5FF; /* Very light blue for subtle highlights */
        --border-color: #DEE2E6; /* Light grey border */
        --shadow: rgba(0, 0, 0, 0.08) 0px 4px 12px 0px; /* Softer, more subtle shadow */
        --hover-shadow: rgba(0, 0, 0, 0.12) 0px 6px 18px 0px; /* Slightly more pronounced on hover */
        --success-bg: #D4EDDA; --success-text: #155724; --success-border: #C3E6CB;
        --error-bg: #F8D7DA; --error-text: #721C24; --error-border: #F5C6CB;
        --info-bg: #D1ECF1; --info-text: #0C5460; --info-border: #BEE5EB;
    """

    dark_theme_vars = """
        --primary-color: #7DB9EE; /* A brighter, yet professional blue for dark theme */
        --secondary-color: #ADB5BD; /* Lighter grey for secondary text */
        --background-color: #212529; /* Darker charcoal for main background */
        --card-background: #2C3034; /* Slightly lighter dark grey for cards */
        --text-color: #E9ECEF; /* Off-white for readability */
        --accent-light: #3A4045; /* Darker muted grey for accents */
        --border-color: #495057; /* Medium dark grey border */
        --shadow: rgba(0, 0, 0, 0.4) 0px 4px 12px; /* More pronounced shadow for dark theme */
        --hover-shadow: rgba(0, 0, 0, 0.6) 0px 6px 18px;
        --success-bg: #284D31; --success-text: #C8E6C9; --success-border: #388E3C;
        --error-bg: #6B2E35; --error-text: #FFCDD2; --error-border: #D32F2F;
        --info-bg: #2A5A6A; --info-text: #BBDEFB; --info-border: #1976D2;
    """

    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Poppins:wght@400;600;700&display=swap');

            /* Apply selected theme variables */
            :root {{
                {"/* Light Theme */" if theme == "light" else "/* Dark Theme */"}
                {light_theme_vars if theme == "light" else dark_theme_vars}
                --border-radius: 0.75rem; /* Slightly more rounded corners */
            }}

            body {{
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 0;
            }}

            /* --- Apply colors and styling using variables --- */
            .stApp {{
                background-color: var(--background-color);
                color: var(--text-color);
                transition: background-color 0.4s ease, color 0.4s ease; /* Smoother transition */
            }}

            /* Main content area styling - removed max-width for full screen */
            .main .block-container {{
                padding-top: 2.5rem; /* Slightly more padding */
                padding-bottom: 2.5rem;
                padding-left: 3rem; /* More horizontal padding */
                padding-right: 3rem;
                max-width: 100%; /* Ensure full width for main content */
            }}

            /* Header styling */
            h1, h2, h3, h4, h5, h6 {{
                color: var(--primary-color);
                font-weight: 600;
                margin-bottom: 1rem;
            }}

            /* Specific styling for brand header and subtitle */
            .brand-header {{
                font-family: 'Poppins', sans-serif;
                font-size: 3.8rem; /* Even larger font size for brand */
                font-weight: 700;
                color: var(--primary-color);
                text-align: center;
                margin-bottom: 0.75rem;
                letter-spacing: 2px;
                text-shadow: 3px 3px 6px rgba(0,0,0,0.2); /* More prominent shadow */
                transition: color 0.4s ease, text-shadow 0.4s ease;
            }}

            .brand-subtitle {{
                font-family: 'Inter', sans-serif;
                font-size: 1.6rem; /* Slightly larger subtitle */
                font-weight: 400;
                color: var(--secondary-color);
                text-align: center;
                margin-top: 0;
                margin-bottom: 2.5rem;
                transition: color 0.4s ease;
            }}

            /* Increased font size for question text */
            .stMarkdown p strong {{
                font-size: 1.3rem; /* Larger font size for questions */
                line-height: 1.6;
                color: var(--text-color); /* Ensure question text uses main text color */
            }}

            /* Card-like containers for sections */
            .stContainer {{
                background-color: var(--card-background);
                padding: 2rem; /* More padding inside cards */
                border-radius: var(--border-radius);
                box-shadow: var(--shadow);
                margin-bottom: 2rem; /* More margin between cards */
                transition: all 0.3s ease-in-out;
            }}
            .stContainer:hover {{
                box-shadow: var(--hover-shadow);
            }}

            /* Buttons */
            .stButton > button {{
                background-color: var(--primary-color);
                color: var(--card-background); /* Button text contrasts with primary color */
                border: none;
                border-radius: var(--border-radius);
                padding: 0.8rem 1.8rem; /* Larger padding for buttons */
                font-weight: 600;
                font-size: 1.05rem; /* Slightly larger button text */
                transition: all 0.2s ease-in-out;
                box-shadow: rgba(0, 0, 0, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.1) 0px 3px 7px -3px; /* More refined shadow */
            }}
            .stButton > button:hover {{
                filter: brightness(1.15); /* Slightly brighter on hover for both themes */
                transform: translateY(-3px); /* More pronounced lift */
                box-shadow: var(--hover-shadow);
            }}
            .stButton > button:active {{
                transform: translateY(0);
                box-shadow: var(--shadow);
            }}

            /* Text Inputs and Text Areas */
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea {{
                border-radius: var(--border-radius);
                border: 1px solid var(--border-color);
                padding: 0.8rem 1.2rem; /* Larger padding for inputs */
                font-family: 'Inter', sans-serif;
                color: var(--text-color);
                background-color: var(--background-color); /* Inputs match app background */
                transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            }}
            .stTextInput > div > div > input:focus,
            .stTextArea > div > div > textarea:focus {{
                border-color: var(--primary-color);
                box-shadow: 0 0 0 0.25rem rgba(var(--primary-color-rgb), 0.25); /* Use primary color for focus outline with transparency */
                outline: none;
            }}
            /* Ensure labels for inputs have correct color */
            .stTextInput label, .stTextArea label {{
                color: var(--text-color);
            }}

            /* Radio Buttons */
            .stRadio > label {{
                font-weight: 400;
                color: var(--text-color);
                font-size: 1.15rem; /* Larger font size for radio options */
            }}
            .stRadio div[role="radiogroup"] label span {{
                border-radius: 50%;
                border: 2px solid var(--primary-color);
                background-color: var(--card-background);
                width: 20px; /* Slightly larger radio button circles */
                height: 20px;
                display: inline-block;
                vertical-align: middle;
                margin-right: 10px; /* More space */
                position: relative;
                transition: all 0.2s ease;
            }}
            .stRadio div[role="radiogroup"] label.st-dg span {{ /* Selected radio button */
                background-color: var(--primary-color);
                border-color: var(--primary-color);
            }}
            .stRadio div[role="radiogroup"] label.st-dg span::after {{
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 10px; /* Larger inner circle */
                height: 10px;
                background-color: var(--card-background);
                border-radius: 50%;
            }}

            /* Expander (for admin section) */
            .streamlit-expanderHeader {{
                background-color: var(--accent-light);
                border-radius: var(--border-radius);
                padding: 0.9rem 1.8rem; /* More padding */
                font-weight: 600;
                color: var(--primary-color);
                border: none;
                box-shadow: var(--shadow);
                transition: all 0.2s ease-in-out;
            }}
            .streamlit-expanderHeader:hover {{
                filter: brightness(1.1); /* Slightly brighter on hover */
                transform: translateY(-2px);
            }}

            /* Sidebar styling */
            .stSidebar > div:first-child {{
                background-color: var(--card-background); /* Sidebar uses card background */
                padding: 2.5rem 2rem; /* More padding */
                box-shadow: var(--shadow);
                border-radius: var(--border-radius);
                transition: background-color 0.4s ease, box-shadow 0.4s ease;
            }}
            .stSidebar .stButton > button {{
                width: 100%;
                margin-bottom: 0.75rem; /* More space between sidebar buttons */
            }}

            /* Metrics */
            [data-testid="stMetric"] {{
                background-color: var(--card-background);
                padding: 1.5rem; /* More padding */
                border-radius: var(--border-radius);
                box-shadow: var(--shadow);
                text-align: center;
                margin-bottom: 1.5rem;
            }}
            [data-testid="stMetric"] > div > div:first-child {{
                color: var(--secondary-color);
                font-size: 1rem; /* Slightly larger label */
            }}
            [data-testid="stMetric"] > div > div:last-child {{
                color: var(--primary-color);
                font-size: 2.2rem; /* Larger value */
                font-weight: 700;
            }}

            /* Success/Error/Info messages */
            .stAlert {{
                border-radius: var(--border-radius);
                padding: 1.2rem; /* More padding */
                margin-bottom: 1.2rem;
                font-size: 1.05rem; /* Slightly larger text */
            }}
            .stAlert.success {{
                background-color: var(--success-bg);
                color: var(--success-text);
                border-color: var(--success-border);
            }}
            .stAlert.error {{
                background-color: var(--error-bg);
                color: var(--error-text);
                border-color: var(--error-border);
            }}
            .stAlert.info {{
                background-color: var(--info-bg);
                color: var(--info-text);
                border-color: var(--info-border);
            }}

            /* Logo Container (for login page) */
            .logo-container {{
                text-align: center;
                margin-bottom: 2.5rem; /* More margin below logo */
                padding-bottom: 1.5rem;
                border-bottom: 1px solid var(--border-color); /* Use dynamic border color */
            }}
            /* Fixed button container at the bottom for quiz */
            .fixed-bottom-buttons {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                width: 100%;
                background-color: var(--card-background); /* Match card background */
                padding: 1rem 2rem;
                box-shadow: rgba(0, 0, 0, 0.2) 0px -5px 15px -3px; /* Shadow above buttons */
                display: flex;
                justify-content: flex-end; /* Align to the right */
                gap: 1rem; /* Space between buttons */
                z-index: 1000; /* Ensure buttons are on top */
                border-top-left-radius: var(--border-radius);
                border-top-right-radius: var(--border-radius);
            }}
            .fixed-bottom-buttons .stButton {{
                flex-grow: 0; /* Prevent buttons from growing */
                flex-shrink: 0; /* Prevent buttons from shrinking */
                width: auto; /* Allow button width to be determined by content + padding */
            }}
            .fixed-bottom-buttons .stButton > button {{
                width: auto; /* Make buttons fill their flex container */
                min-width: 180px; /* Ensure a minimum width for better appearance */
            }}

            /* Adjust main content padding when fixed buttons are present */
            .main {{
                padding-bottom: 6rem; /* Add padding to main content to prevent overlap with fixed buttons */
            }}

            /* Hide the internal Streamlit buttons that are triggered by custom HTML */
            /* Targeting the container div of the button by its data-testid */
            [data-testid="stButton-submit_answer_internal_btn"],
            [data-testid="stButton-next_question_internal_btn"] {{
                display: none !important;
            }}
            /* Hide the internal submit/next/finish button that is triggered by custom HTML */
            [data-testid="stButton-next_question_submit_quiz_internal_btn"] {{
                display: none !important;
            }}
        </style>
    """, unsafe_allow_html=True)

# --- Helper Functions for JSON files ---
def load_json_file(filepath, default_content={}):
    """Loads data from a JSON file, creating it with default content if it doesn't exist."""
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            json.dump(default_content, f, indent=2)
        return default_content
    with open(filepath, "r") as f:
        return json.load(f)

def save_json_file(filepath, data):
    """Saves data to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

# --- Session State Initialization ---
def initialize_session_state():
    """Initializes all necessary session state variables and loads data."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = None # 'admin' or 'student'
    if "username" not in st.session_state:
        st.session_state.username = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home" # Default page after login
    if "theme" not in st.session_state:
        st.session_state.theme = "light" # Default theme

    # Student Quiz State
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    if "current_quiz_id" not in st.session_state:
        st.session_state.current_quiz_id = None
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "attempted_questions_count" not in st.session_state:
        st.session_state.attempted_questions_count = 0
    if "student_answers" not in st.session_state:
        # Stores (question_index, selected_option, correct_option_string, is_correct) for current quiz
        st.session_state.student_answers = []
    if "show_explanation" not in st.session_state:
        st.session_state.show_explanation = False
    if "selected_option" not in st.session_state:
        st.session_state.selected_option = None # No option selected by default
    if "feedback_message" not in st.session_state:
        st.session_state.feedback_message = ""
    if "quiz_completed" not in st.session_state:
        st.session_state.quiz_completed = False

    # Data loaded from files
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "r") as f:
            initial_questions_data = json.load(f)
        if isinstance(initial_questions_data, list):
            # This conversion warning should now appear after set_page_config
            st.warning(f"Converting '{QUESTIONS_FILE}' from old list format to new multi-quiz format. Please review.")
            initial_questions_data = {"SAP Security Quiz": initial_questions_data}
            save_json_file(QUESTIONS_FILE, initial_questions_data)
    else:
        initial_questions_data = {"SAP Security Quiz": []}
        save_json_file(QUESTIONS_FILE, initial_questions_data)

    st.session_state.questions = initial_questions_data
    st.session_state.users = load_json_file(USERS_FILE, {"admin": {"password": "adminpassword", "role": "admin"}})
    st.session_state.user_progress = load_json_file(USER_PROGRESS_FILE, {})


def reset_quiz_state():
    """Resets quiz-specific session state variables for a new quiz."""
    st.session_state.quiz_started = False
    st.session_state.current_question_index = 0
    st.session_state.score = 0
    st.session_state.attempted_questions_count = 0
    st.session_state.student_answers = []
    st.session_state.show_explanation = False
    st.session_state.selected_option = None # Ensure no option is selected for a new question
    st.session_state.feedback_message = ""
    st.session_state.quiz_completed = False

# --- Logo Placeholder ---
def display_logo():
    st.markdown("""
        <div class="logo-container">
            <h1 class="brand-header">NeuroverseAI</h1>
            <p class="brand-subtitle">GenAI & SAP Training</p>
        </div>
    """, unsafe_allow_html=True)

# --- Login Page ---
def login_page():
    """Displays the login form."""
    display_logo()
    
    # Use a container for the login card
    with st.container():
        st.markdown("<h2 style='text-align: center; color: var(--primary-color);'>🔐 Quiz Platform Login</h2>", unsafe_allow_html=True)
        st.markdown("---")
        with st.form("login_form"):
            username = st.text_input("User ID", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submit_button = st.form_submit_button("Login")

            if submit_button:
                users_data = st.session_state.users
                user = users_data.get(username)

                if user and user["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user_role = user["role"]
                    st.session_state.username = username
                    st.session_state.current_page = "Home" # Navigate to home after login
                    st.success(f"Welcome, {username}!")

                    # Initialize user progress for this user if not exists
                    if username not in st.session_state.user_progress:
                         st.session_state.user_progress[username] = {}
                    save_json_file(USER_PROGRESS_FILE, st.session_state.user_progress)
                    st.rerun()
                else:
                    st.error("Invalid User ID or Password.")

# --- Home Page ---
def home_page():
    st.title(f"Welcome, {st.session_state.username}!")
    st.header("NeuroverseAI Training Platform")
    st.write("This platform provides quizzes to test your knowledge in GenAI and SAP.")
    st.markdown("---")
    st.subheader("What would you like to do?")
    if st.session_state.user_role == 'student':
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Take a Quiz"):
                st.session_state.current_page = "Take Quiz"
                st.rerun()
        with col2:
            if st.button("View My Scores"):
                st.session_state.current_page = "View My Scores"
                st.rerun()
    elif st.session_state.user_role == 'admin':
        st.write("Use the sidebar to navigate to Admin actions.")

# --- Helper function for Next Question / Submit Quiz internal button ---
def handle_next_or_finish_quiz_button(is_last_question):
    """Handles the logic for the Next Question or Submit Quiz button."""
    if is_last_question:
        st.session_state.quiz_completed = True
    else:
        st.session_state.current_question_index += 1
    st.session_state.show_explanation = False
    st.session_state.selected_option = None # Clear selection for next question
    st.session_state.feedback_message = ""

# --- Student Quiz Flow ---
def student_quiz_page():
    """Manages the student's quiz experience."""
    st.title(f"Take a Quiz, {st.session_state.username}!")

    available_quizzes = list(st.session_state.questions.keys())
    if not available_quizzes:
        st.warning("No quizzes available. Please ask an administrator to add questions.")
        return

    # Quiz selection
    if st.session_state.current_quiz_id is None:
        st.subheader("Select a Quiz")
        selected_quiz = st.selectbox("Choose a quiz to start:", available_quizzes, key="quiz_selector")
        if st.button("Start Selected Quiz"):
            st.session_state.current_quiz_id = selected_quiz
            reset_quiz_state() # Reset state for the new quiz
            st.session_state.quiz_started = True
            st.rerun()
        return

    # Once a quiz is selected and started
    current_quiz_id = st.session_state.current_quiz_id
    questions = st.session_state.questions.get(current_quiz_id, [])
    total_questions = len(questions)

    if not questions:
        st.warning(f"No questions found for '{current_quiz_id}'. Please select another quiz or ask an administrator to add questions.")
        st.session_state.current_quiz_id = None # Allow re-selection
        return

    st.header(f"Quiz: {current_quiz_id}")

    # Display progress bar
    st.progress((st.session_state.current_question_index) / total_questions, text=f"Progress: {st.session_state.current_question_index}/{total_questions} questions answered.")


    # Check if the student has already completed THIS quiz
    user_quiz_progress = st.session_state.user_progress.get(st.session_state.username, {}).get(current_quiz_id, {})
    if isinstance(user_quiz_progress, dict) and user_quiz_progress.get("attempted", False) and user_quiz_progress.get("total", 0) == total_questions:
        st.info(f"You have already completed the '{current_quiz_id}' quiz.")
        col_score, col_accuracy = st.columns(2)
        with col_score:
            st.metric("Your Previous Score", f"{user_quiz_progress['score']} / {user_quiz_progress['total']}")
        with col_accuracy:
            prev_accuracy = (user_quiz_progress['score'] / user_quiz_progress['total'] * 100) if user_quiz_progress['total'] > 0 else 0
            st.metric("Your Previous Accuracy", f"{prev_accuracy:.2f}%")
        st.write("You can view detailed results in 'View My Scores'.")
        if st.button("Choose another Quiz"):
            st.session_state.current_quiz_id = None
            st.session_state.quiz_started = False
            st.rerun()
        return

    if st.session_state.quiz_completed:
        display_quiz_dashboard(total_questions, current_quiz_id)
        # Update user progress for the specific quiz
        if st.session_state.username not in st.session_state.user_progress:
            st.session_state.user_progress[st.session_state.username] = {}
        st.session_state.user_progress[st.session_state.username][current_quiz_id] = {
            "score": st.session_state.score,
            "total": total_questions,
            "attempted": True,
            "answers_log": st.session_state.student_answers # Save detailed log
        }
        save_json_file(USER_PROGRESS_FILE, st.session_state.user_progress)
        st.success(f"Your results for '{current_quiz_id}' have been saved!")

        if st.button("Take another Quiz"):
            st.session_state.current_quiz_id = None
            st.session_state.quiz_started = False
            st.rerun()
        return

    current_q_index = st.session_state.current_question_index

    if current_q_index >= total_questions:
        st.session_state.quiz_completed = True
        st.rerun() # Rerun to display dashboard
        return

    current_question = questions[current_q_index]
    is_last_question = (current_q_index + 1 == total_questions)

    def update_selected_option_and_record():
        # This callback updates st.session_state.selected_option
        # with the value from the radio button when its value changes.
        st.session_state.selected_option = st.session_state[f"radio_q_{st.session_state.current_question_index}_{current_quiz_id}"]

    with st.container():
        st.subheader(f"Question {current_q_index + 1} of {total_questions}")
        st.markdown(f"**{current_question['question']}**")

        # Determine initial index for st.radio
        # It should be None by default, and only set if an option was previously selected
        initial_radio_index = None
        if st.session_state.selected_option in current_question["options"]:
            initial_radio_index = current_question["options"].index(st.session_state.selected_option)

        st.radio(
            "Select your answer:",
            current_question["options"],
            index=initial_radio_index, # Use the determined initial index
            key=f"radio_q_{current_q_index}_{current_quiz_id}", # Unique key for the radio button
            on_change=update_selected_option_and_record, # Call this function when radio selection changes
            disabled=st.session_state.show_explanation # Disable after submission
        )

        # Submit Answer button (below options, not fixed)
        if not st.session_state.show_explanation:
            if st.button(
                "Submit Answer",
                key="submit_answer_button",
                disabled=st.session_state.selected_option is None,
                on_click=lambda q=current_question: st.session_state.update(
                    attempted_questions_count=st.session_state.attempted_questions_count + 1,
                    score=st.session_state.score + (1 if st.session_state.selected_option == q["correct_option"] else 0),
                    feedback_message="✅ Correct!" if st.session_state.selected_option == q["correct_option"] else f"❌ Wrong! The correct answer was: **{q['correct_option']}**",
                    show_explanation=True,
                    student_answers=st.session_state.student_answers + [{
                        "question": q["question"],
                        "selected_answer": st.session_state.selected_option,
                        "correct_answer": q["correct_option"],
                        "is_correct": (st.session_state.selected_option == q["correct_option"]),
                        "explanation": q["explanation"]
                    }]
                )
            ):
                pass # This block is necessary for Streamlit button to trigger on_click

        # Display feedback and explanation
        if st.session_state.show_explanation:
            st.write(st.session_state.feedback_message)
            st.info(f"Explanation: {current_question['explanation']}")

    # Fixed bottom button for Next Question / Submit Quiz
    if st.session_state.show_explanation: # Only show after an answer has been submitted
        next_or_finish_button_text = "Submit Quiz" if is_last_question else "Next Question"
        # Using a container with custom HTML to apply fixed positioning and right alignment
        st.markdown('<div class="fixed-bottom-buttons">', unsafe_allow_html=True)
        if st.button(
            next_or_finish_button_text,
            key="next_question_submit_quiz_button",
            on_click=lambda: handle_next_or_finish_quiz_button(is_last_question) # Pass is_last_question
        ):
            pass # This block is necessary for Streamlit button to trigger on_click
        st.markdown('</div>', unsafe_allow_html=True)


def display_quiz_dashboard(total_questions, quiz_id):
    """Displays the final quiz dashboard."""
    st.subheader(f"Quiz Completed: {quiz_id}!")
    
    col_score, col_accuracy, col_attempted = st.columns(3)
    with col_score:
        st.metric(label="Total Score", value=f"{st.session_state.score} / {total_questions}")
    with col_accuracy:
        accuracy = (st.session_state.score / st.session_state.attempted_questions_count * 100) if st.session_state.attempted_questions_count > 0 else 0
        st.metric(label="Accuracy", value=f"{round(accuracy, 2)}%")
    with col_attempted:
        st.metric(label="Questions Attempted", value=st.session_state.attempted_questions_count)

    st.write("---")
    st.subheader("Your Answers:")
    for i, answer_log in enumerate(st.session_state.student_answers):
        with st.container():
            status_icon = "✅" if answer_log["is_correct"] else "❌"
            st.markdown(f"**Q{i+1}:** {answer_log['question']}")
            st.markdown(f"Your Answer: **{answer_log['selected_answer']}** {status_icon}")
            if not answer_log["is_correct"]:
                st.markdown(f"Correct Answer: **{answer_log['correct_answer']}**")
            # Fetch original explanation if available in questions_sample.json
            original_question_data = next((q for q in st.session_state.questions.get(quiz_id, []) if q['question'] == answer_log['question']), None)
            if original_question_data and original_question_data.get('explanation'):
                st.info(f"Explanation: {original_question_data['explanation']}")
            st.markdown("---")

def view_my_scores_page():
    st.title(f"My Quiz Scores, {st.session_state.username}!")
    
    user_progress = st.session_state.user_progress.get(st.session_state.username, {})
    
    if not user_progress:
        st.info("You haven't attempted any quizzes yet.")
        return

    attempted_quizzes_summary = []
    for quiz_id, data in user_progress.items():
        # Ensure 'data' is a dictionary before trying to use .get()
        if isinstance(data, dict) and data.get("attempted"):
            accuracy = (data['score'] / data['total'] * 100) if data['total'] > 0 else 0
            attempted_quizzes_summary.append({
                "Quiz Name": quiz_id,
                "Score": f"{data['score']} / {data['total']}",
                "Accuracy": f"{accuracy:.2f}%"
            })
    
    if not attempted_quizzes_summary:
        st.info("You haven't completed any quizzes yet.")
        return

    st.subheader("Summary of Completed Quizzes")
    df_summary = pd.DataFrame(attempted_quizzes_summary)
    st.dataframe(df_summary, hide_index=True)

    st.markdown("---")
    st.subheader("Review Past Quiz Attempts")
    
    # Filter for quizzes with detailed answer logs
    quizzes_with_logs = [q_id for q_id, data in user_progress.items() if isinstance(data, dict) and data.get("answers_log")]
    
    if not quizzes_with_logs:
        st.info("No detailed quiz logs available for review.")
        return

    selected_quiz_to_review = st.selectbox("Select a completed quiz to review:", quizzes_with_logs, key="review_quiz_selector")

    if selected_quiz_to_review:
        quiz_log = user_progress[selected_quiz_to_review]["answers_log"]
        total_questions_reviewed = user_progress[selected_quiz_to_review]["total"]
        score_reviewed = user_progress[selected_quiz_to_review]["score"]

        st.markdown(f"#### Detailed Review for: {selected_quiz_to_review}")
        st.metric("Score", f"{score_reviewed} / {total_questions_reviewed}")

        for i, answer_log in enumerate(quiz_log):
            with st.container():
                status_icon = "✅" if answer_log["is_correct"] else "❌"
                st.markdown(f"**Q{i+1}:** {answer_log['question']}")
                st.markdown(f"Your Answer: **{answer_log['selected_answer']}** {status_icon}")
                if not answer_log["is_correct"]:
                    st.markdown(f"Correct Answer: **{answer_log['correct_answer']}**")
                # Fetch original explanation if available in questions_sample.json
                original_question_data = next((q for q in st.session_state.questions.get(selected_quiz_to_review, []) if q['question'] == answer_log['question']), None)
                if original_question_data and original_question_data.get('explanation'):
                    st.info(f"Explanation: {original_question_data['explanation']}")
                st.markdown("---")


# --- Admin Flow ---
def admin_page():
    """Manages the admin panel for questions and performance."""
    st.title(f"Welcome, {st.session_state.username} (Admin)!")

    st.sidebar.header("Admin Actions")
    admin_action = st.sidebar.radio(
        "Choose an action:",
        ["Manage Questions", "Manage Users", "View Trainee Performance"],
        key="admin_sidebar_radio" # Unique key for admin sidebar
    )

    if admin_action == "Manage Questions":
        manage_questions_section()
    elif admin_action == "Manage Users":
        manage_users_section()
    elif admin_action == "View Trainee Performance":
        view_trainee_performance_section()

def manage_questions_section():
    """Admin section for adding, editing, and deleting questions."""
    st.header("Manage Quiz Questions")

    # Admin can select which quiz to manage questions for
    quiz_ids = list(st.session_state.questions.keys())
    
    new_quiz_name_input = st.text_input("Create New Quiz Name:", key="new_quiz_name_input")
    if st.button("Create Quiz", key="create_new_quiz_button"):
        if new_quiz_name_input:
            if new_quiz_name_input in st.session_state.questions:
                st.error(f"Quiz '{new_quiz_name_input}' already exists.")
            else:
                st.session_state.questions[new_quiz_name_input] = []
                save_json_file(QUESTIONS_FILE, st.session_state.questions)
                st.success(f"Quiz '{new_quiz_name_input}' created. You can now add questions to it.")
                st.rerun()
        else:
            st.error("Please enter a name for the new quiz.")

    if not quiz_ids:
        st.info("No quizzes defined yet. Create one above to start adding questions.")
        return

    selected_quiz_for_management = st.selectbox("Select Quiz to Manage:", quiz_ids, key="manage_quiz_selector")
    questions_for_selected_quiz = st.session_state.questions.get(selected_quiz_for_management, [])

    # --- Delete Quiz Section ---
    if selected_quiz_for_management:
        st.markdown("---")
        st.subheader(f"Danger Zone: Delete '{selected_quiz_for_management}' Quiz")
        # Use a checkbox for confirmation to avoid accidental clicks
        confirm_delete_quiz_checkbox = st.checkbox(f"I understand that deleting '{selected_quiz_for_management}' is irreversible and will remove all associated student progress.", key=f"confirm_delete_quiz_checkbox_{selected_quiz_for_management}")
        if st.button(f"Delete Quiz '{selected_quiz_for_management}' Permanently", key=f"delete_quiz_button_{selected_quiz_for_management}", disabled=not confirm_delete_quiz_checkbox):
            if confirm_delete_quiz_checkbox:
                del st.session_state.questions[selected_quiz_for_management]
                save_json_file(QUESTIONS_FILE, st.session_state.questions)
                
                # Remove associated user progress for this quiz
                for user_id in list(st.session_state.user_progress.keys()): # Iterate over a copy of keys
                    if selected_quiz_for_management in st.session_state.user_progress[user_id]:
                        del st.session_state.user_progress[user_id][selected_quiz_for_management]
                save_json_file(USER_PROGRESS_FILE, st.session_state.user_progress)
                
                st.success(f"Quiz '{selected_quiz_for_management}' and its associated progress deleted successfully.")
                st.session_state.current_quiz_id = None # Clear current quiz if it was deleted
                st.rerun()
            else:
                st.error("Please confirm deletion by checking the box.")
        st.markdown("---")


    with st.container():
        st.subheader(f"Add New Question to '{selected_quiz_for_management}'")
        with st.form("add_question_form"):
            new_question_text = st.text_area("Question Text", key="add_q_text")
            # Allow adding fewer than 4 options initially
            new_options_inputs = []
            for i in range(4): # Provide inputs for up to 4 options
                option_value = st.text_input(f"Option {i+1}", key=f"add_opt_{i}")
                if option_value: # Only add non-empty options
                    new_options_inputs.append(option_value)

            new_correct_option = st.selectbox("Correct Option", options=new_options_inputs if new_options_inputs else ["Select an option"], key="add_correct_opt")
            new_explanation = st.text_area("Explanation", key="add_explanation")
            add_button = st.form_submit_button("Add Question")

            if add_button:
                if not (new_question_text and new_options_inputs and new_correct_option and new_explanation):
                    st.error("Please fill in all mandatory fields (Question, at least one Option, Correct Option, and Explanation).")
                elif new_correct_option not in new_options_inputs:
                    st.error("Correct option must be one of the provided options.")
                else:
                    new_q = {
                        "question": new_question_text,
                        "options": new_options_inputs, # Save only the provided options
                        "correct_option": new_correct_option, # Storing as string
                        "explanation": new_explanation
                    }
                    st.session_state.questions[selected_quiz_for_management].append(new_q)
                    save_json_file(QUESTIONS_FILE, st.session_state.questions)
                    st.success("Question added successfully!")
                    st.rerun()

    st.subheader(f"Existing Questions in '{selected_quiz_for_management}'")
    if not questions_for_selected_quiz:
        st.info("No questions available for this quiz. Add some using the form above.")
        return

    for i, q in enumerate(questions_for_selected_quiz):
        with st.container():
            with st.expander(f"Question {i+1}: {q['question'][:70]}..."): # Truncate for display
                st.write(f"**Question:** {q['question']}")
                st.write(f"**Options:** {', '.join(q['options'])}")
                st.write(f"**Correct Option:** {q['correct_option']}")
                st.write(f"**Explanation:** {q['explanation']}")

                st.markdown("---")
                st.write("Edit this question:")
                edited_question = st.text_area("Question Text", value=q["question"], key=f"edit_q_text_{selected_quiz_for_management}_{i}")
                
                # Dynamically generate text inputs for existing options, and empty for up to 4 if less exist
                edited_options = []
                for j in range(max(len(q["options"]), 4)): # Ensure at least 4 input fields are shown for editing
                    option_value = q["options"][j] if j < len(q["options"]) else ""
                    edited_option_input = st.text_input(f"Option {j+1}", value=option_value, key=f"edit_opt_{selected_quiz_for_management}_{i}_{j}")
                    if edited_option_input: # Only include non-empty options in the final list
                        edited_options.append(edited_option_input)

                try:
                    # Find the index of the current correct option within the *edited* options
                    current_correct_index = edited_options.index(q["correct_option"])
                except ValueError:
                    # If the correct option string is not found in the current edited options, default to the first option or None
                    current_correct_index = 0 if edited_options else None

                edited_correct_option = st.selectbox(
                    "Correct Option",
                    options=edited_options if edited_options else ["Select an option"],
                    index=current_correct_index,
                    key=f"edit_correct_opt_{selected_quiz_for_management}_{i}"
                )
                edited_explanation = st.text_area("Explanation", value=q["explanation"], key=f"edit_explanation_{selected_quiz_for_management}_{i}")

                col_edit, col_delete = st.columns(2)
                with col_edit:
                    if st.button("Save Changes", key=f"save_q_{selected_quiz_for_management}_{i}"):
                        if not (edited_question and edited_options and edited_correct_option and edited_explanation):
                            st.error("Please fill in all mandatory fields (Question, at least one Option, Correct Option, and Explanation).")
                        elif edited_correct_option not in edited_options:
                            st.error("Correct option must be one of the provided options.")
                        else:
                            st.session_state.questions[selected_quiz_for_management][i] = {
                                "question": edited_question,
                                "options": edited_options, # Save only the valid, non-empty options
                                "correct_option": edited_correct_option,
                                "explanation": edited_explanation
                            }
                            save_json_file(QUESTIONS_FILE, st.session_state.questions)
                            st.success(f"Question {i+1} updated successfully!")
                            st.rerun()
                with col_delete:
                    if st.button("Delete Question", key=f"delete_q_{selected_quiz_for_management}_{i}"):
                        st.session_state.questions[selected_quiz_for_management].pop(i)
                        save_json_file(QUESTIONS_FILE, st.session_state.questions)
                        st.warning(f"Question {i+1} deleted from '{selected_quiz_for_management}'.")
                        st.rerun()

def manage_users_section():
    """Admin section to create student accounts and manage existing ones."""
    st.header("Manage User Accounts")

    with st.container():
        st.subheader("Create New Student Account")
        with st.form("create_student_form"):
            new_username = st.text_input("New Student User ID", key="new_student_username")
            new_password = st.text_input("New Student Password", type="password", key="new_student_password")
            create_button = st.form_submit_button("Create Student Account")

            if create_button:
                if new_username and new_password:
                    if new_username in st.session_state.users:
                        st.error(f"User ID '{new_username}' already exists.")
                    else:
                        st.session_state.users[new_username] = {"password": new_password, "role": "student"}
                        save_json_file(USERS_FILE, st.session_state.users)
                        # Initialize progress for the new student
                        if new_username not in st.session_state.user_progress:
                            st.session_state.user_progress[new_username] = {} # Initialize as empty dict for quizzes
                            save_json_file(USER_PROGRESS_FILE, st.session_state.user_progress)
                        st.success(f"Student account '{new_username}' created successfully!")
                        st.rerun()
                else:
                    st.error("Please provide both username and password.")

    st.subheader("Existing Users")
    if not st.session_state.users:
        st.info("No users found.")
        return

    # Display users with a delete option
    # Create columns for header
    col_header_user, col_header_role, col_header_action = st.columns([0.4, 0.3, 0.3])
    with col_header_user:
        st.markdown("**Username**")
    with col_header_role:
        st.markdown("**Role**")
    with col_header_action:
        st.markdown("**Action**")
    st.markdown("---")

    for u in list(st.session_state.users.keys()): # Iterate over a copy of keys for safe deletion
        user_data = st.session_state.users[u]
        col_user, col_role, col_delete_btn = st.columns([0.4, 0.3, 0.3])
        
        with col_user:
            st.write(u)
        with col_role:
            st.write(user_data["role"])
        
        with col_delete_btn:
            if u == st.session_state.username: # Current logged-in admin cannot delete themselves
                st.info("Current User")
            elif user_data["role"] == "admin": # Prevent deleting other admins for simplicity
                 st.info("Admin User")
            else:
                # Use a unique key for each delete checkbox and button
                delete_key_checkbox = f"delete_user_checkbox_{u}"
                delete_key_button = f"delete_user_button_{u}"

                confirm_delete_user_checkbox = st.checkbox(f"Confirm delete {u}", key=delete_key_checkbox)
                if st.button(f"Delete {u}", key=delete_key_button, disabled=not confirm_delete_user_checkbox):
                    if confirm_delete_user_checkbox:
                        del st.session_state.users[u]
                        save_json_file(USERS_FILE, st.session_state.users)
                        # Remove user's progress data
                        if u in st.session_state.user_progress:
                            del st.session_state.user_progress[u]
                            save_json_file(USER_PROGRESS_FILE, st.session_state.user_progress)
                        st.success(f"User '{u}' and their progress deleted successfully.")
                        st.rerun()
                    else:
                        st.error("Please confirm deletion by checking the box.")
        st.markdown("---")


def view_trainee_performance_section():
    """Admin section for viewing and downloading trainee performance, categorized by attempted status."""
    st.header("Trainee Performance Overview")

    all_users = st.session_state.users
    user_progress = st.session_state.user_progress

    attempted_students_summary = []
    not_attempted_students = []

    for username, user_data in all_users.items():
        if user_data["role"] == "student":
            student_quizzes_progress = user_progress.get(username, {})
            
            has_attempted_any_quiz = False
            for quiz_id, quiz_data in student_quizzes_progress.items():
                # Ensure quiz_data is a dictionary before trying to use .get()
                if isinstance(quiz_data, dict) and quiz_data.get("attempted"):
                    has_attempted_any_quiz = True
                    accuracy = (quiz_data['score'] / quiz_data['total'] * 100) if quiz_data['total'] > 0 else 0
                    attempted_students_summary.append({
                        "Student ID": username,
                        "Quiz Name": quiz_id,
                        "Score": f"{quiz_data['score']} / {quiz_data['total']}",
                        "Accuracy": f"{accuracy:.2f}%"
                    })
            if not has_attempted_any_quiz:
                not_attempted_students.append({"Student ID": username})

    with st.container():
        st.subheader("✅ Students Who Attempted Quizzes")
        if attempted_students_summary:
            df_attempted = pd.DataFrame(attempted_students_summary)
            st.dataframe(df_attempted, hide_index=True)
            csv_data_attempted = df_attempted.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Attempted Students Data (CSV)",
                data=csv_data_attempted,
                file_name="attempted_students_performance.csv",
                mime="text/csv",
            )
        else:
            st.info("No students have attempted any quizzes yet.")

    with st.container():
        st.subheader("❌ Students Who Haven't Attempted Any Quiz")
        if not_attempted_students:
            df_not_attempted = pd.DataFrame(not_attempted_students)
            st.dataframe(df_not_attempted, hide_index=True)
            csv_data_not_attempted = df_not_attempted.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Not Attempted Students Data (CSV)",
                data=csv_data_not_attempted,
                file_name="not_attempted_students.csv",
                mime="text/csv",
            )
        else:
            st.info("All students have attempted at least one quiz.")

# --- Main Application Logic ---
def main():
    # set_page_config must be the first Streamlit command
    # Set layout to "wide" for full screen and sidebar to "collapsed" for mobile view
    st.set_page_config(page_title="NeuroverseAI Quiz", layout="wide", initial_sidebar_state="collapsed")
    
    # Initialize session state and load data
    initialize_session_state() 

    # Apply custom CSS immediately after page config, passing the current theme
    apply_custom_css(st.session_state.theme)

    # Sidebar for logout and navigation
    with st.sidebar:
        # Theme toggle button
        if st.session_state.theme == "light":
            if st.button("🌙 Switch to Dark Mode"):
                st.session_state.theme = "dark"
                st.rerun()
        else:
            if st.button("☀️ Switch to Light Mode"):
                st.session_state.theme = "light"
                st.rerun()

        if st.session_state.logged_in:
            display_logo() # Logo in sidebar after login
            st.write(f"Logged in as: **{st.session_state.username}** ({st.session_state.user_role.capitalize()})")
            st.markdown("---")
            
            if st.session_state.user_role == 'student':
                st.header("Navigation")
                if st.button("Home", key="nav_home"):
                    st.session_state.current_page = "Home"
                    st.session_state.current_quiz_id = None # Reset quiz selection
                    reset_quiz_state()
                    st.rerun()
                if st.button("Take Quiz", key="nav_take_quiz"):
                    st.session_state.current_page = "Take Quiz"
                    st.session_state.current_quiz_id = None # Reset quiz selection
                    reset_quiz_state()
                    st.rerun()
                if st.button("View My Scores", key="nav_view_scores"):
                    st.session_state.current_page = "View My Scores"
                    st.session_state.current_quiz_id = None # Reset quiz selection
                    reset_quiz_state()
                    st.rerun()
            elif st.session_state.user_role == 'admin':
                st.header("Admin Panel")
                if st.button("Manage Questions", key="admin_nav_manage_questions"):
                    st.session_state.current_page = "Manage Questions"
                    st.rerun()
                if st.button("Manage Users", key="admin_nav_manage_users"):
                    st.session_state.current_page = "Manage Users"
                    st.rerun()
                if st.button("View Trainee Performance", key="admin_nav_view_performance"):
                    st.session_state.current_page = "View Trainee Performance"
                    st.rerun()
            
            st.markdown("---")
            if st.button("Logout", key="sidebar_logout_button"):
                st.session_state.logged_in = False
                st.session_state.user_role = None
                st.session_state.username = None
                st.session_state.current_page = "Login" # Go to login page on logout
                reset_quiz_state() # Clear quiz state on logout
                st.rerun()
        else:
            # Only show logo and theme toggle on login page if not logged in
            display_logo() 

    # Main content area based on current_page
    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.current_page == "Home":
            home_page()
        elif st.session_state.current_page == "Take Quiz" and st.session_state.user_role == 'student':
            student_quiz_page()
        elif st.session_state.current_page == "View My Scores" and st.session_state.user_role == 'student':
            view_my_scores_page()
        elif st.session_state.current_page == "Manage Questions" and st.session_state.user_role == 'admin':
            manage_questions_section()
        elif st.session_state.current_page == "Manage Users" and st.session_state.user_role == 'admin':
            manage_users_section()
        elif st.session_state.current_page == "View Trainee Performance" and st.session_state.user_role == 'admin':
            view_trainee_performance_section()
        else:
            # Fallback for unexpected page/role combinations, redirect to home
            st.session_state.current_page = "Home"
            st.rerun()


if __name__ == "__main__":
    main()
