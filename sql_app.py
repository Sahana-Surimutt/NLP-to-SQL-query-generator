import streamlit as st
import sqlite3
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Model name
MODEL = "llama-3.3-70b-versatile"

# Database path
DB_PATH = "employee.db"

# Example questions
EXAMPLE_QUESTIONS = [
    "Show all employees",
    "Who is the oldest employee?",
    "Show me all data engineers",
    "What is the average age of employees?",
    "How many employees are in each designation?",
    "Show employees older than 30",
    "Who is the youngest data scientist"
]


def is_safe_query(sql_query):
    """
    Validate that the SQL query is safe
    """

    upper_query = sql_query.upper().strip()

    # Remove markdown formatting
    upper_query = upper_query.replace("```SQL", "")
    upper_query = upper_query.replace("```", "")

    if not upper_query.startswith("SELECT"):
        return False

    dangerous_keywords = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "CREATE",
        "ALTER",
        "TRUNCATE",
        "EXECUTE",
        "UNION",
        "--"
    ]

    query_without_select = upper_query[6:]

    for keyword in dangerous_keywords:
        if keyword in query_without_select:
            return False

    if sql_query.strip().count(";") > 1:
        return False

    return True


def get_schema_context():
    """
    Read schema information
    """

    try:
        with open("schema.txt", "r") as f:
            return f.read()

    except FileNotFoundError:

        return """
        Table: EMPLOYEE

        Columns:
        EMP_NAME (VARCHAR)
        EMP_ID (VARCHAR)
        DESIGNATION (VARCHAR)
        EMP_AGE (INT)
        """


def generate_sql_with_guardrails(natural_language_query):
    """
    Generate SQL query using Groq
    """

    schema_context = get_schema_context()

    system_prompt = f"""
    You are a SQL query generator.

    STRICT RULES:
    1. Generate ONLY SELECT queries
    2. Do NOT generate INSERT, UPDATE, DELETE, DROP
    3. Use ONLY EMPLOYEE table
    4. Return ONLY SQL query
    5. Use SQLite syntax
    6. No markdown
    7. If invalid request return:
       ERROR: Invalid request

    Database Schema:
    {schema_context}

    IMPORTANT:
    Return ONLY SQL query.
    """

    try:

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": natural_language_query
                }
            ],
            temperature=0.1,
            max_tokens=150
        )

        sql_query = response.choices[0].message.content.strip()

        # Remove markdown formatting if generated
        sql_query = sql_query.replace("```sql", "")
        sql_query = sql_query.replace("```", "")
        sql_query = sql_query.strip()

        # Safety check
        if not is_safe_query(sql_query):
            return "ERROR: Unsafe query generated", False

        return sql_query, True

    except Exception as e:

        return f"ERROR: {str(e)}", False


def execute_query(sql_query):
    """
    Execute SQL query
    """

    try:

        conn = sqlite3.connect(DB_PATH)

        cursor = conn.cursor()

        cursor.execute(sql_query)

        results = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ]

        conn.close()

        return results, columns, True, ""

    except Exception as e:

        return [], [], False, str(e)


def main():

    st.set_page_config(
        page_title="NLP to SQL Query Generator",
        layout="wide"
    )

    st.title("🤖 NLP to SQL Query Generator")

    st.subheader(
        "Convert Natural Language into SQL Queries"
    )

    # Check API key
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:

        st.error(
            "❌ GROQ_API_KEY not found in .env file"
        )

        st.stop()

    col1, col2 = st.columns([2, 1])

    with col1:

        st.markdown("### 💬 Ask Your Question")

        user_question = st.text_area(
            "Enter your question:",
            placeholder="Example: Show all employees older than 30",
            height=100
        )

        st.markdown("#### 🤔 Example Questions")

        example_cols = st.columns(2)

        for i, example in enumerate(EXAMPLE_QUESTIONS):

            col_idx = i % 2

            if example_cols[col_idx].button(
                example,
                key=f"example_{i}"
            ):

                st.session_state["question"] = example

        if "question" in st.session_state:

            user_question = st.session_state["question"]

        if st.button(
            "🚀 Generate SQL Query",
            type="primary"
        ):

            if user_question.strip():

                with st.spinner(
                    "Generating SQL query..."
                ):

                    sql_query, success = (
                        generate_sql_with_guardrails(
                            user_question
                        )
                    )

                    if success:

                        st.session_state[
                            "generated_sql"
                        ] = sql_query

                        st.session_state[
                            "error"
                        ] = None

                    else:

                        st.session_state[
                            "error"
                        ] = sql_query

                        st.session_state[
                            "generated_sql"
                        ] = None

            else:

                st.warning(
                    "Please enter a question first!"
                )

    with col2:

        st.markdown("### 📊 Database Schema")

        with st.expander("View Schema"):

            st.code(get_schema_context())

    # Display SQL query
    if (
        "generated_sql" in st.session_state
        and st.session_state["generated_sql"]
    ):

        st.markdown("---")

        st.markdown("### 🔍 Generated SQL Query")

        sql_query = st.session_state["generated_sql"]

        st.code(sql_query, language="sql")

        # Execute query button
        if st.button("▶️ Execute Query"):

            with st.spinner("Executing query..."):

                results, columns, success, error_msg = (
                    execute_query(sql_query)
                )

                if success:

                    st.markdown("### 📈 Query Results")

                    if results:

                        st.markdown(
                            "**Columns:** "
                            + ", ".join(columns)
                        )

                        st.markdown("**Results:**")

                        for i, row in enumerate(results, 1):

                            row_dict = dict(
                                zip(columns, row)
                            )

                            st.text(
                                f"{i}. {row_dict}"
                            )

                        st.success(
                            f"✅ Found {len(results)} row(s)"
                        )

                    else:

                        st.info(
                            "No results found."
                        )

                else:

                    st.error(
                        f"❌ Query execution failed: {error_msg}"
                    )

    elif (
        "error" in st.session_state
        and st.session_state["error"]
    ):

        st.markdown("---")

        st.error(st.session_state["error"])


if __name__ == "__main__":
    main()

