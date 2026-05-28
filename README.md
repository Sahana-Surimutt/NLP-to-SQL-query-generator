# NLP-to-SQL-query-generator
AI-powered NLP to SQL Query Generator using Python, Streamlit, OpenAI, and SQLite for converting natural language into SQL queries.

# 🧠 NLP to SQL 

An intelligent Natural Language Processing (NLP) based SQL Query Generator that converts human language queries into SQL commands and retrieves data from a SQLite database.

This project allows users to interact with databases using plain English instead of writing SQL manually.

---

## 🚀 Features

* Convert natural language into SQL queries
* Execute generated SQL queries on SQLite database
* Employee database integration
* Simple and beginner-friendly implementation
* Fast query processing
* Easy database customization
* Streamlit-based interactive UI

---

## 🛠️ Technologies Used

* Python
* SQLite
* Streamlit
* OpenAI API
* NLP
* python-dotenv

Dependencies from `requirements.txt`:

---

## 📂 Project Structure

```plaintext
NL_SQL/
│
├── sql_app.py              # Main application
├── sql_data_insert.py      # Database creation and sample data insertion
├── employee.db             # SQLite database
├── schema.txt              # Database schema information
├── requirements.txt        # Project dependencies
├── README.md               # Documentation
```

---

## 🗄️ Database Schema

The project uses an `EMPLOYEE` table with the following columns:

| Column Name | Data Type   | Description   |
| ----------- | ----------- | ------------- |
| EMP_NAME    | VARCHAR(25) | Employee Name |
| EMP_ID      | VARCHAR(25) | Employee ID   |
| DESIGNATION | VARCHAR(25) | Employee Role |
| EMP_AGE     | INT         | Employee Age  |

Schema reference:

---

## 📊 Sample Data

The database contains employee records such as:

* NLP Engineer
* Data Engineer
* Data Scientist
* Cloud Engineer

Inserted using `sql_data_insert.py`:

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Sahana-Surimutt/NLP-to-SQL-query-generator.git
cd NLP-to-SQL-query-generator
```

---

### 2️⃣ Create Virtual Environment (Optional)

```bash
python -m venv venv
```

Activate environment:

#### Windows

```bash
venv\Scripts\activate
```

#### Linux/Mac

```bash
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configure Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
```

---

### 5️⃣ Run the Application

```bash
streamlit run sql_app.py
```

---

## 💡 Example Queries

Try asking:

* Show all employees
* List all Data Engineers
* Find employees older than 35
* Show employee names and IDs
* Count number of employees
* Who is the oldest employee?

---

## 🔄 How It Works

1. User enters a natural language query
2. NLP processes the input
3. OpenAI generates the SQL query
4. SQL query is executed on SQLite database
5. Results are displayed to the user

---

## 🔮 Future Enhancements

* Support for MySQL and PostgreSQL
* Voice-based query input
* Advanced NLP models
* Authentication system
* Query history tracking
* Data visualization dashboard

---

## 📌 Use Cases

* Database learning and education
* SQL beginners
* Business data querying
* NLP-based database interaction
* AI-powered analytics tools
---

## 📜 License

This project is open-source and available under the MIT License.

---

