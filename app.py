import streamlit as st
import json
import pandas as pd
import os
import time

# --- Configuration ---
QUESTIONS_FILE = "questions_sample.json"
USERS_FILE = "users.json"
USER_PROGRESS_FILE = "user_progress.json"

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

# --- Initial Setup ---
# Ensure essential files exist on first run
load_json_file(QUESTIONS_FILE, []) # questions_sample.json might be empty initially or from previous run
load_json_file(USERS_FILE, {"admin": {"password": "adminpassword", "role": "admin"}}) # Default admin user
load_json_file(USER_PROGRESS_FILE, {})

# --- Session State Initialization ---
def initialize_session_state():
    """Initializes all necessary session state variables."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = None # 'admin' or 'student'
    if "username" not in st.session_state:
        st.session_state.username = None

    # Student Quiz State
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "attempted_questions_count" not in st.session_state:
        st.session_state.attempted_questions_count = 0
    if "student_answers" not in st.session_state:
        # Stores (question_index, selected_option, correct_option_string, is_correct)
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
    st.session_state.questions = load_json_file(QUESTIONS_FILE)
    st.session_state.users = load_json_file(USERS_FILE)
    st.session_state.user_progress = load_json_file(USER_PROGRESS_FILE)

def reset_quiz_state():
    """Rests quiz-specific session state variables for a new quiz."""
    st.session_state.quiz_started = False
    st.session_state.current_question_index = 0
    st.session_state.score = 0
    st.session_state.attempted_questions_count = 0
    st.session_state.student_answers = []
    st.session_state.show_explanation = False
    st.session_state.selected_option = None
    st.session_state.feedback_message = ""
    st.session_state.quiz_completed = False

# --- Login Page ---
def login_page():
    """Displays the login form."""
    st.title("🔐 NeuroverseAI Quiz Platform Login")

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
                st.success(f"Welcome, {username}!")

                # Initialize user progress if not exists
                if username not in st.session_state.user_progress:
                    st.session_state.user_progress[username] = {
                        "score": 0,
                        "total": len(st.session_state.questions),
                        "attempted": False
                    }
                    save_json_file(USER_PROGRESS_FILE, st.session_state.user_progress)
                st.rerun()
            else:
                st.error("Invalid User ID or Password.")

# --- Student Quiz Flow ---
def student_quiz_page():
    """Manages the student's quiz experience."""
    st.title(f"Welcome, {st.session_state.username}!")
    st.header("SAP Training Quiz")

    questions = st.session_state.questions
    total_questions = len(questions)

    if not questions:
        st.warning("No quiz questions available. Please ask an administrator to add questions.")
        return

    # Check if the student has already completed the quiz
    if st.session_state.user_progress.get(st.session_state.username, {}).get("attempted", False) and \
       st.session_state.user_progress[st.session_state.username]["total"] == total_questions:
        st.info("You have already completed this quiz.")
        # Display their previous results
        prev_score = st.session_state.user_progress[st.session_state.username]["score"]
        prev_total = st.session_state.user_progress[st.session_state.username]["total"]
        prev_accuracy = (prev_score / prev_total * 100) if prev_total > 0 else 0
        st.metric("Your Previous Score", f"{prev_score} / {prev_total}")
        st.metric("Your Previous Accuracy", f"{prev_accuracy:.2f}%")
        st.write("You can contact your administrator for more details.")
        return # Prevent starting a new quiz if already completed

    if not st.session_state.quiz_started:
        st.write("Click 'Start Quiz' to begin your assessment.")
        if st.button("Start Quiz"):
            reset_quiz_state() # Ensure fresh quiz state for a new attempt
            st.session_state.quiz_started = True
            st.rerun()
        return

    if st.session_state.quiz_completed:
        display_quiz_dashboard(total_questions)
        # Update user progress in user_progress.json
        st.session_state.user_progress[st.session_state.username] = {
            "score": st.session_state.score,
            "total": total_questions,
            "attempted": True
        }
        save_json_file(USER_PROGRESS_FILE, st.session_state.user_progress)
        st.success("Your quiz results have been saved!")

        if st.button("Logout", key="logout_button_quiz_complete"): # Offer logout after completion
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.username = None
            reset_quiz_state()
            st.rerun()
        return

    current_q_index = st.session_state.current_question_index

    if current_q_index >= total_questions:
        st.session_state.quiz_completed = True
        st.rerun() # Rerun to display dashboard
        return

    current_question = questions[current_q_index]

    st.subheader(f"Question {current_q_index + 1} of {total_questions}")
    st.write(current_question["question"])

    # Use a unique key for the radio button to prevent issues on re-renders
    # Disable radio buttons after submission to prevent re-selection
    selected_option = st.radio(
        "Select your answer:",
        current_question["options"],
        key=f"q_{current_q_index}",
        disabled=st.session_state.show_explanation
    )
    st.session_state.selected_option = selected_option # Store selection in session state

    col1, col2 = st.columns(2)

    with col1:
        # Only allow submission if explanation is not currently shown
        if st.button("Submit Answer", disabled=st.session_state.show_explanation):
            st.session_state.attempted_questions_count += 1
            # Compare selected option directly with the correct_option string
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
            st.rerun() # Rerun to show feedback and explanation

    # Display explanation and "Next Question" button only after submission
    if st.session_state.show_explanation:
        st.write(st.session_state.feedback_message)
        st.info(f"Explanation: {current_question['explanation']}")

        with col2:
            if st.button("Next Question"):
                st.session_state.current_question_index += 1
                st.session_state.show_explanation = False
                st.session_state.selected_option = None # Clear selection for next question
                st.session_state.feedback_message = ""
                st.rerun()

def display_quiz_dashboard(total_questions):
    """Displays the final quiz dashboard."""
    st.subheader("Quiz Completed!")
    st.metric(label="Total Score", value=f"{st.session_state.score} / {total_questions}")

    accuracy = (st.session_state.score / st.session_state.attempted_questions_count * 100) if st.session_state.attempted_questions_count > 0 else 0
    st.metric(label="Accuracy", value=f"{round(accuracy, 2)}%")
    st.metric(label="Questions Attempted", value=st.session_state.attempted_questions_count)

    st.write("---")
    st.subheader("Your Answers:")
    for i, answer_log in enumerate(st.session_state.student_answers):
        status_icon = "✅" if answer_log["is_correct"] else "❌"
        st.write(f"**Q{i+1}:** {answer_log['question']}")
        st.write(f"Your Answer: {answer_log['selected_answer']} {status_icon}")
        if not answer_log["is_correct"]:
            st.write(f"Correct Answer: {answer_log['correct_answer']}")
        st.markdown("---")


# --- Admin Flow ---
def admin_page():
    """Manages the admin panel for questions and performance."""
    st.title(f"Welcome, {st.session_state.username} (Admin)!")

    st.sidebar.header("Admin Actions")
    admin_action = st.sidebar.radio(
        "Choose an action:",
        ["Manage Questions", "Manage Users", "View Trainee Performance"]
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

    questions = st.session_state.questions

    st.subheader("Add New Question")
    with st.form("add_question_form"):
        new_question_text = st.text_area("Question Text", key="add_q_text")
        new_options = [st.text_input(f"Option {i+1}", key=f"add_opt_{i}") for i in range(4)]
        # Ensure correct option is selected from the provided options
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
                questions.append(new_q)
                save_json_file(QUESTIONS_FILE, questions)
                st.session_state.questions = questions # Update session state
                st.success("Question added successfully!")
                st.rerun()


    st.subheader("Existing Questions")
    if not questions:
        st.info("No questions available. Add some using the form above.")
        return

    # Display questions in an editable format
    for i, q in enumerate(questions):
        with st.expander(f"Question {i+1}: {q['question'][:70]}..."): # Truncate for display
            st.write(f"**Question:** {q['question']}")
            st.write(f"**Options:** {', '.join(q['options'])}")
            st.write(f"**Correct Option:** {q['correct_option']}")
            st.write(f"**Explanation:** {q['explanation']}")

            st.markdown("---")
            st.write("Edit this question:")
            edited_question = st.text_area("Question Text", value=q["question"], key=f"edit_q_text_{i}")
            edited_options = [st.text_input(f"Option {j+1}", value=q["options"][j], key=f"edit_opt_{i}_{j}") for j in range(4)]

            # Find the index of the current correct option to pre-select it
            try:
                current_correct_index = edited_options.index(q["correct_option"])
            except ValueError:
                current_correct_index = 0 # Fallback if original correct option is not found in edited options

            edited_correct_option = st.selectbox(
                "Correct Option",
                options=edited_options if edited_options else ["Select an option"],
                index=current_correct_index,
                key=f"edit_correct_opt_{i}"
            )
            edited_explanation = st.text_area("Explanation", value=q["explanation"], key=f"edit_explanation_{i}")

            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.button("Save Changes", key=f"save_q_{i}"):
                    if edited_correct_option not in edited_options:
                        st.error("Correct option must be one of the provided options.")
                    else:
                        questions[i] = {
                            "question": edited_question,
                            "options": edited_options,
                            "correct_option": edited_correct_option, # Storing as string
                            "explanation": edited_explanation
                        }
                        save_json_file(QUESTIONS_FILE, questions)
                        st.session_state.questions = questions # Update session state
                        st.success(f"Question {i+1} updated successfully!")
                        st.rerun()
            with col_delete:
                if st.button("Delete Question", key=f"delete_q_{i}"):
                    questions.pop(i)
                    save_json_file(QUESTIONS_FILE, questions)
                    st.session_state.questions = questions # Update session state
                    st.warning(f"Question {i+1} deleted.")
                    st.rerun()

def manage_users_section():
    """Admin section to create student accounts."""
    st.header("Manage User Accounts")

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
                    st.session_state.user_progress[new_username] = {
                        "score": 0,
                        "total": len(st.session_state.questions),
                        "attempted": False
                    }
                    save_json_file(USER_PROGRESS_FILE, st.session_state.user_progress)
                    st.success(f"Student account '{new_username}' created successfully!")
                    st.rerun()
            else:
                st.error("Please provide both username and password.")

    st.subheader("Existing Users")
    users_df = pd.DataFrame([
        {"Username": u, "Role": d["role"]}
        for u, d in st.session_state.users.items()
    ])
    st.dataframe(users_df)

def view_trainee_performance_section():
    """Admin section for viewing and downloading trainee performance, categorized by attempted status."""
    st.header("Trainee Performance Overview")

    all_users = st.session_state.users
    user_progress = st.session_state.user_progress

    attempted_students = []
    not_attempted_students = []

    for username, user_data in all_users.items():
        if user_data["role"] == "student":
            progress = user_progress.get(username)
            if progress and progress["attempted"]:
                attempted_students.append({
                    "Student ID": username,
                    "Score": progress["score"],
                    "Total Questions": progress["total"],
                    "Accuracy": f"{ (progress['score'] / progress['total'] * 100):.2f}%" if progress['total'] > 0 else "0.00%"
                })
            else:
                not_attempted_students.append({"Student ID": username})

    st.subheader("✅ Students Who Attempted the Quiz")
    if attempted_students:
        df_attempted = pd.DataFrame(attempted_students)
        st.dataframe(df_attempted)
        csv_data_attempted = df_attempted.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Attempted Students Data (CSV)",
            data=csv_data_attempted,
            file_name="attempted_students_performance.csv",
            mime="text/csv",
        )
    else:
        st.info("No students have attempted the quiz yet.")

    st.subheader("❌ Students Who Haven't Attempted the Quiz")
    if not_attempted_students:
        df_not_attempted = pd.DataFrame(not_attempted_students)
        st.dataframe(df_not_attempted)
        csv_data_not_attempted = df_not_attempted.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Not Attempted Students Data (CSV)",
            data=csv_data_not_attempted,
            file_name="not_attempted_students.csv",
            mime="text/csv",
        )
    else:
        st.info("All students have attempted the quiz.")

# --- Main Application Logic ---
def main():
    st.set_page_config(page_title="NeuroverseAI Quiz", layout="centered")
    initialize_session_state()

    if not st.session_state.logged_in:
        login_page()
    else:
        st.sidebar.write(f"Logged in as: **{st.session_state.username}** ({st.session_state.user_role.capitalize()})")
        if st.sidebar.button("Logout", key="sidebar_logout_button"): # Added unique key here
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.username = None
            reset_quiz_state() # Clear quiz state on logout
            st.rerun()

        if st.session_state.user_role == 'student':
            student_quiz_page()
        elif st.session_state.user_role == 'admin':
            admin_page()

if __name__ == "__main__":
    main()
