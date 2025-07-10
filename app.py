import streamlit as st
import json
import pandas as pd
import os
import time

# --- Configuration ---
QUESTIONS_FILE = "questions_sample.json"
USERS_FILE = "users.json"
USER_PROGRESS_FILE = "user_progress.json"

# --- Custom CSS for a Clean, Modern, and Professional Look ---
def apply_custom_css():
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

            :root {{
                --primary-color: #66b3ff; /* Lighter Blue - Stands out on dark background */
                --secondary-color: #b0c4de; /* Light Blue-Grey - For secondary text and subtle elements */
                --background-color: #282c34; /* Deep Charcoal/Dark Blue - Main background */
                --card-background: #3a404c; /* Slightly Lighter Dark Grey - Cards stand out from background */
                --text-color: #f0f2f6; /* Off-White - Highly readable text on dark background */
                --accent-light: #4c5360; /* Muted Dark Grey - For subtle accents like expander headers */
                --border-radius: 10px;
                --shadow: rgba(0, 0, 0, 0.3) 0px 4px 12px; /* More pronounced shadow for dark theme */
                --hover-shadow: rgba(0, 0, 0, 0.45) 0px 8px 20px;
            }}

            body {{
                font-family: 'Inter', sans-serif;
                color: var(--text-color);
                background-color: var(--background-color);
            }}

            .stApp {{
                background-color: var(--background-color);
            }}

            /* Main content area styling */
            .main .block-container {{
                padding-top: 2rem;
                padding-bottom: 2rem;
                padding-left: 2rem;
                padding-right: 2rem;
                max-width: 1200px; /* Limit content width for better readability */
            }}

            /* Header styling */
            h1, h2, h3, h4, h5, h6 {{
                color: var(--primary-color);
                font-weight: 600;
                margin-bottom: 1rem;
            }}

            /* Card-like containers for sections */
            .stContainer {{
                background-color: var(--card-background);
                padding: 1.5rem;
                border-radius: var(--border-radius);
                box-shadow: var(--shadow);
                margin-bottom: 1.5rem;
                transition: all 0.3s ease-in-out;
            }}
            .stContainer:hover {{
                box-shadow: var(--hover-shadow);
            }}

            /* Buttons */
            .stButton > button {{
                background-color: var(--primary-color);
                color: var(--text-color); /* Button text is light */
                border: none;
                border-radius: var(--border-radius);
                padding: 0.75rem 1.5rem;
                font-weight: 600;
                transition: all 0.2s ease-in-out;
                box-shadow: rgba(0, 0, 0, 0.2) 0px 4px 6px -1px, rgba(0, 0, 0, 0.1) 0px 2px 4px -1px;
            }}
            .stButton > button:hover {{
                background-color: #4da6ff; /* Slightly brighter primary on hover */
                transform: translateY(-2px);
                box-shadow: rgba(0, 0, 0, 0.3) 0px 8px 10px -2px, rgba(0, 0, 0, 0.15) 0px 4px 6px -2px;
            }}
            .stButton > button:active {{
                transform: translateY(0);
                box_shadow: var(--shadow);
            }}

            /* Text Inputs and Text Areas */
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea {{
                border-radius: var(--border-radius);
                border: 1px solid #636e72; /* Darker border for contrast */
                padding: 0.75rem 1rem;
                font-family: 'Inter', sans-serif;
                color: var(--text-color);
                background-color: var(--background-color); /* Use background color for inputs */
                transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            }}
            .stTextInput > div > div > input:focus,
            .stTextArea > div > div > textarea:focus {{
                border-color: var(--primary-color);
                box-shadow: 0 0 0 0.2rem rgba(102, 179, 255, 0.25); /* Primary color alpha */
                outline: none;
            }}

            /* Radio Buttons */
            .stRadio > label {{
                font-weight: 400;
                color: var(--text-color);
            }}
            .stRadio div[role="radiogroup"] label span {{
                border-radius: 50%;
                border: 2px solid var(--primary-color);
                background-color: var(--card-background); /* White for radio circle */
                width: 18px;
                height: 18px;
                display: inline-block;
                vertical-align: middle;
                margin-right: 8px;
                position: relative;
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
                width: 8px;
                height: 8px;
                background-color: var(--card-background); /* Inner dot is card background color */
                border-radius: 50%;
            }}

            /* Expander (for admin section) */
            .streamlit-expanderHeader {{
                background-color: var(--accent-light);
                border-radius: var(--border-radius);
                padding: 0.75rem 1.5rem;
                font-weight: 600;
                color: var(--primary-color);
                border: none;
                box-shadow: var(--shadow);
                transition: all 0.2s ease-in-out;
            }}
            .streamlit-expanderHeader:hover {{
                background-color: #5a6473; /* Slightly darker accent on hover */
                transform: translateY(-1px);
            }}

            /* Sidebar styling */
            .stSidebar > div:first-child {{
                background-color: var(--card-background);
                padding: 2rem 1.5rem;
                box-shadow: var(--shadow);
                border-radius: var(--border-radius);
            }}
            .stSidebar .stButton > button {{
                width: 100%;
                margin-bottom: 0.5rem;
            }}

            /* Metrics */
            [data-testid="stMetric"] {{
                background-color: var(--card-background);
                padding: 1rem;
                border-radius: var(--border-radius);
                box-shadow: var(--shadow);
                text-align: center;
                margin-bottom: 1rem;
            }}
            [data-testid="stMetric"] > div > div:first-child {{
                color: var(--secondary-color);
                font-size: 0.9rem;
            }}
            [data-testid="stMetric"] > div > div:last-child {{
                color: var(--primary-color);
                font-size: 2rem;
                font-weight: 700;
            }}

            /* Success/Error/Info messages */
            .stAlert {{
                border-radius: var(--border-radius);
                padding: 1rem;
                margin-bottom: 1rem;
            }}
            .stAlert.success {{
                background-color: #386641; /* Darker green */
                color: #e6ffe6; /* Lighter text */
                border-color: #5cb85c;
            }}
            .stAlert.error {{
                background-color: #8c2f39; /* Darker red */
                color: #ffe6e6; /* Lighter text */
                border-color: #d9534f;
            }}
            .stAlert.info {{
                background-color: #2a6f8f; /* Darker blue */
                color: #e6f7ff; /* Lighter text */
                border-color: #5bc0de;
            }}

            /* Logo Placeholder */
            .logo-container {{
                text-align: center;
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid #4a4e5a; /* Darker border for logo separator */
            }}
            .logo-placeholder {{
                font-size: 2.5rem;
                font-weight: 700;
                color: var(--primary-color);
                text-transform: uppercase;
                letter-spacing: 2px;
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
        st.session_state.selected_option = None
    if "feedback_message" not in st.session_state:
        st.session_state.feedback_message = ""
    if "quiz_completed" not in st.session_state:
        st.session_state.quiz_completed = False

    # Data loaded from files
    # This block is moved here to ensure it runs AFTER set_page_config
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
    st.session_state.selected_option = None
    st.session_state.feedback_message = ""
    st.session_state.quiz_completed = False

# --- Logo Placeholder ---
def display_logo():
    st.markdown("""
        <div class="logo-container">
            <div class="logo-placeholder">NeuroverseAI</div>
            <p style="color: var(--secondary-color); font-size: 0.9rem; margin-top: 5px;">GenAI & SAP Training</p>
        </div>
    """, unsafe_allow_html=True)

# --- Login Page ---
def login_page():
    """Displays the login form."""
    display_logo()
    st.title("🔐 Quiz Platform Login")

    with st.container():
        st.markdown("### Enter your credentials")
        with st.form("login_form"):
            username = st.text_input("User ID")
            password = st.text_input("Password", type="password")
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

    # Check if the student has already completed THIS quiz
    user_quiz_progress = st.session_state.user_progress.get(st.session_state.username, {}).get(current_quiz_id, {})
    if user_quiz_progress.get("attempted", False) and user_quiz_progress.get("total", 0) == total_questions:
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

    with st.container():
        st.subheader(f"Question {current_q_index + 1} of {total_questions}")
        st.markdown(f"**{current_question['question']}**")

        selected_option = st.radio(
            "Select your answer:",
            current_question["options"],
            key=f"q_{current_q_index}_{current_quiz_id}", # Unique key for each question in each quiz
            disabled=st.session_state.show_explanation
        )
        st.session_state.selected_option = selected_option # Store selection in session state

        col_submit, col_next = st.columns(2)

        with col_submit:
            if st.button("Submit Answer", disabled=st.session_state.show_explanation):
                st.session_state.attempted_questions_count += 1
                is_correct = (st.session_state.selected_option == current_question["correct_option"])

                if is_correct:
                    st.session_state.score += 1
                    st.session_state.feedback_message = "✅ Correct!"
                else:
                    st.session_state.feedback_message = f"❌ Wrong! The correct answer was: **{current_question['correct_option']}**"

                st.session_state.student_answers.append({
                    "question_index": current_q_index,
                    "question": current_question["question"],
                    "selected_answer": st.session_state.selected_option,
                    "correct_answer": current_question["correct_option"],
                    "is_correct": is_correct
                })
                st.session_state.show_explanation = True
                st.rerun()

        if st.session_state.show_explanation:
            st.write(st.session_state.feedback_message)
            st.info(f"Explanation: {current_question['explanation']}")

            with col_next:
                if st.button("Next Question"):
                    st.session_state.current_question_index += 1
                    st.session_state.show_explanation = False
                    st.session_state.selected_option = None
                    st.session_state.feedback_message = ""
                    st.rerun()

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

    with st.container():
        st.subheader(f"Add New Question to '{selected_quiz_for_management}'")
        with st.form("add_question_form"):
            new_question_text = st.text_area("Question Text", key="add_q_text")
            new_options = [st.text_input(f"Option {i+1}", key=f"add_opt_{i}") for i in range(4)]
            new_correct_option = st.selectbox("Correct Option", options=new_options if new_options[0] else ["Select an option"], key="add_correct_opt")
            new_explanation = st.text_area("Explanation", key="add_explanation")
            add_button = st.form_submit_button("Add Question")

            if add_button:
                if not (new_question_text and all(new_options) and new_correct_option and new_explanation):
                    st.error("Please fill in all fields to add a question.")
                elif new_correct_option not in new_options:
                    st.error("Correct option must be one of the provided options.")
                else:
                    new_q = {
                        "question": new_question_text,
                        "options": new_options,
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
                edited_options = [st.text_input(f"Option {j+1}", value=q["options"][j], key=f"edit_opt_{selected_quiz_for_management}_{i}_{j}") for j in range(4)]

                try:
                    current_correct_index = edited_options.index(q["correct_option"])
                except ValueError:
                    current_correct_index = 0

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
                        if edited_correct_option not in edited_options:
                            st.error("Correct option must be one of the provided options.")
                        else:
                            st.session_state.questions[selected_quiz_for_management][i] = {
                                "question": edited_question,
                                "options": edited_options,
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
    """Admin section to create student accounts."""
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

    with st.container():
        st.subheader("Existing Users")
        users_df = pd.DataFrame([
            {"Username": u, "Role": d["role"]}
            for u, d in st.session_state.users.items()
        ])
        st.dataframe(users_df, hide_index=True)

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
    st.set_page_config(page_title="NeuroverseAI Quiz", layout="centered", initial_sidebar_state="expanded")
    apply_custom_css() # Apply custom CSS at the very beginning

    initialize_session_state() # This now handles all file loading and initial data setup

    # Sidebar for logout and navigation
    with st.sidebar:
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
            display_logo() # Logo in sidebar on login page

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
