# 🍳 Chefbot  

Chef bot is a rule-based recipe recommendation chatbot with a Flask backend and React (Vite)
frontend

## Prerequisites

Before running the project, make sure you have the following installed:

- Python 3.10+
- Node.js 18+
- pip (python package manager)
- npm (node package manager)
- Flask and Flask-cors python packages

## Installation

From project root (/ChefBot)

1.Backend dependencies

```text
cd backend
pip install flask flask-cors
```

2.Frontend dependencies

```text
cd ../frontend
npm install
```

Now you can use any methods below.

---

## How to run

### Recommended (All platforms)

From project root (/ChefBot), run:

```text
python start.py
```

This will start Flask backend on port 5000 and Vite frontend on port 5173

When you see something like:

```text
 VITE v5.4.21  ready in 227 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

- Type 'o' in the terminal and press enter

- or open URL in browser to use ChefBot.

When you're done

- close website
- Go back to the same terminal, click on it, and press ctrl+c once to stop both servers

### Second Method (sets up both ports at the same time)

Enter

```text
./setup.sh
chmod +x start.sh
./ start.sh
```

If it says that ports could not be be set public, manually change port visibility of ports 5000 and 5173 to public

### Manually (Two terminals)

Starting backend and frontend seperatly in two terminals

### Terminal 1 - Backend

From the project root:

```text
cd backend
python app.py  
```

This command starts the Flask backend server. You should then see something like.

```text
* Serving Flask app 'app'
* Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 ```

### Terminal 2 - Frontend

In a second terminal from the project root (/ChefBot)

```text
cd frontend
npm run dev
```

This command starts the React (Vite) frontend. You should see something like

```bash
 VITE v5.4.21  ready in 227 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help

```

Once both servers are running, open <http://localhost:5173> in your browser to use the chatbot.

Note (GitHub Codespaces):

- Ensure ports 5000 and 5173 are set to public.
- If needed, update the backendURL in your front end so it matches the backendURL provided by codespaces.
