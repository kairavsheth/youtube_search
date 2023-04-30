# Endpoints

- `/api/fetch`: Fetches all the entries from Youtube based on the search query.
- `/api/list`: List all the entries from the database. Optional query parameter with key - "search"

Fuzzy search still under dev

# Setup

1. Clone repo
2. Install requirements using `pip install -r requirements.txt`
3. Rename `.envtemplate` to `.env`
4. Create a database on a postgreSQL server
5. Migrate the database using
    ```
    py manage.py makemigrations
    py manage.py migrate
    ```
6. Obtain an API key from GCP console 
7. Replace all the placeholders in the `.env` file
8. Run the server using
    ```
   py manage.py runserver
   ```