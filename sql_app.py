import streamlit as st
import sqlite3
from openai import OpenAI #class
import os
from dotenv import load_dotenv #function
import re

#Load environment variables
load_dotenv()

#Configure OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL","gpt-3.5-turbo")

#Datbase path
DB_PATH="employee.db"

#Example questions for the UI
EXAMPLE_QUESTIONS=[
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
    Validate that the SQL query is safe (SELECT only)
    Returns True if safe, False otherwise
    """
    # Convert to uppercase for case-insensitive checking
    upper_query = sql_query.upper().strip()
    
    # Check if query starts with SELECT
    if not upper_query.startswith("SELECT"):
        return False
    
    # Check for dangerous keywords
    dangerous_keywords = [
        "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", 
        "ALTER", "TRUNCATE", "EXECUTE", "UNION", "--"
    ]
    
    # Remove SELECT from the list temporarily to check other keywords
    query_without_select = upper_query[6:]  # Remove "SELECT"
    
    for keyword in dangerous_keywords:
        if keyword in query_without_select:
            return False
    
    # Check for multiple statements (semicolon)
    if sql_query.strip().count(';') > 1:
        return False
    
    return True

def get_schema_context():
    """Read and return the schema information"""
    try:
        with open("schema.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return """Table: EMPLOYEE
            Columns: EMP_NAME (VARCHAR), EMP_ID (VARCHAR), DESIGNATION (VARCHAR), EMP_AGE (INT)"""
    
def generate_sql_with_guardrails(natural_language_query):
    """
    Generate SQL query using OpenAI with guardrails
    """
    schema_context = get_schema_context()
    
    system_prompt = f"""You are a SQL query generator that converts natural language to SQL.
    
    STRICT RULES - YOU MUST FOLLOW THESE:
    1. Generate ONLY SELECT queries - NO INSERT, UPDATE, DELETE, DROP, or any data modification
    2. Use ONLY the EMPLOYEE table provided in the schema
    3. Return ONLY the SQL query, no explanations, no markdown, no additional text
    4. If the request asks for anything other than SELECT queries, respond with: ERROR: Invalid request
    5. Use proper SQL syntax for SQLite
    6. For aggregation queries, use appropriate functions (COUNT, AVG, MAX, MIN, etc.)
    7. Always use single quotes for string literals
    8. Table name is EMPLOYEE (all caps)
    
    Schema Context:
    {schema_context}
    
    Remember: Your response must be ONLY a valid SELECT SQL query or ERROR: Invalid request"""
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": natural_language_query}
            ],
            temperature=0.1,  # Low temperature for more deterministic output #creativity not required
            max_tokens=150
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        # Additional safety check
        if not is_safe_query(sql_query):
            return "ERROR: Generated query failed safety check. Only SELECT queries are allowed.", False
            
        return sql_query, True
        
    except Exception as e:
        return f"ERROR: Failed to generate SQL query - {str(e)}", False
    
def execute_query(sql_query):
    """
    Execute the SQL query and return results
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        conn.close()
        return results, columns, True, ""
        
    except Exception as e:
        return [], [], False, str(e)

def main():
    st.set_page_config(page_title="Natural Language to SQL Q&A", layout="wide")
    
    st.title("🤖 Natural Language to SQL Query Generator")
    st.subheader("Ask questions about employee data in plain English")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Create two columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Ask Your Question")
        
        # Text area for natural language query
        user_question = st.text_area(
            "Enter your question about employee data:",
            placeholder="e.g., Who is the oldest employee?",
            height=100
        )
        
        # Example questions as buttons
        st.markdown("#### 🤔 Try these examples:")
        example_cols = st.columns(2)
        for i, example in enumerate(EXAMPLE_QUESTIONS):
            col_idx = i % 2
            if example_cols[col_idx].button(example, key=f"example_{i}"):
                user_question = example
                st.session_state['question'] = example
        
        # Use session state to persist the question if set by button
        if 'question' in st.session_state and not user_question:
            user_question = st.session_state['question']
        
        # Generate SQL button
        if st.button("🚀 Generate SQL Query", type="primary"):
            if user_question.strip():
                with st.spinner("Generating SQL query..."):
                    sql_query, success = generate_sql_with_guardrails(user_question)
                    
                    if success and not sql_query.startswith("ERROR"):
                        st.session_state['generated_sql'] = sql_query
                        st.session_state['error'] = None
                    else:
                        st.session_state['error'] = sql_query
                        st.session_state['generated_sql'] = None
            else:
                st.warning("Please enter a question first!")
    
    with col2:
        st.markdown("### 📊 Database Schema")
        with st.expander("View Schema Details"):
            st.code(get_schema_context(), language="text")
    
    # Display results section
    if 'generated_sql' in st.session_state and st.session_state['generated_sql']:
        st.markdown("---")
        st.markdown("### 🔍 Generated SQL Query")
        
        sql_query = st.session_state['generated_sql']
        st.code(sql_query, language="sql")
        
        # Execute query button
        if st.button("▶️ Execute Query"):
            with st.spinner("Executing query..."):
                results, columns, success, error_msg = execute_query(sql_query)
                
                if success:
                    st.markdown("### 📈 Query Results")
                    
                    if results:
                        # Display results using plain text format (pandas-free)
                        st.markdown("**Columns:** " + ", ".join(columns))
                        st.markdown("**Results:**")
                        for i, row in enumerate(results, 1):
                            row_dict = dict(zip(columns, row))
                            st.text(f"{i}. {row_dict}")
                        
                        # Show result count
                        st.success(f"✅ Query executed successfully! Found {len(results)} row(s)")
                    else:
                        st.info("ℹ️ Query executed successfully but returned no results.")
                else:
                    st.error(f"❌ Query execution failed: {error_msg}")
    
    elif 'error' in st.session_state and st.session_state['error']:
        st.markdown("---")
        st.error(f"❌ {st.session_state['error']}")

if __name__ == "__main__":
    main()