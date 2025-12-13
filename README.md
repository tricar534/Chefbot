# 🍳 Chefbot  

Chefbot is a rule-based recipe recommendation chatbot with a Flask backend and React (Vite) frontend.

## Prerequisites

Before running the project, make sure you have the following installed:

- Python 3.10+
- Node.js 18+
- pip
- npm
- Flask and Flask-cors python packages

## Installation

From project root (/ChefBot)

1. **Backend dependencies**

```bash
cd backend
pip install flask flask-cors
```

2. **Frontend dependencies**

```bash
cd ../frontend
npm install
```

Now you can use any methods below.

---

## How to run
It is recommended to use Visual Studio Code for running the project files.

### Recommended (All platforms)

From project root (/ChefBot), run:

```bash
python start.py
```

This will start Flask backend on port 5000 and Vite frontend on port 5173

When you see something like:

```bash
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

```bash
./setup.sh
chmod +x start.sh
./ start.sh
```

If it says that ports could not be be set public, manually change port visibility of ports 5000 and 5173 to public

### Manually (Two terminals)

Starting backend and frontend separately in two terminals

### Terminal 1 - Backend

From the project root (/ChefBot):

```bash
cd backend
python app.py  
```

This command starts the Flask backend server. You should then see something like.

```bash
* Serving Flask app 'app'
* Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 ```

### Terminal 2 - Frontend

In a second terminal from the project root (/ChefBot)

```bash
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

## Troubleshooting

Port Already in Use:

- Backend (5000):  
  python -m flask run --port 5001  
  
- Frontend (5173):  
  npm run dev -- --port=5174  

Script Permission Denied:<br>
- chmod +x setup.sh<br>
- chmod +x start.sh

---
Note (GitHub Codespaces):

- Ensure ports 5000 and 5173 are set to public.
- If needed, update the backendURL in your front end so it matches the backendURL provided by Codespaces.

## How to use Chefbot

Once the app is running, you can talk to Chefbot. Here are some exmaple messages you can try:

### Greetings

- `hi`
- `hello`
- `hey chefbot`

### Ingredient-based recipe search

- `I have chicken and rice`
- `I have pasta and tomato sauce`
- `I have chicken, rice and eggs`
- `ihave tuna and mayo`

### Diet preferences

- `vegan please`
- `vegetarian recipes`
- `low carb ideas`
- `high protein meals`
- `keto options`

After you set a diet, Chefbot will try to prioritize recipes that match that diet for the rest of the session.

### Diet + ingredients together

- `I want a vegan meal with rice`
- `I want a vegetarian meal with pasta and tomatoes`
- `I want a keto recipe with chicken and broccoli`
- `I want a low carb meal with eggs and cheese`

These messages both set a diet and tell Chefbot what ingredients you have.

### Recipe details

If Chefbot shows a list of numbered recipes, you can ask for details by number:

- `show me 3`
- `recipe 2`
- `3`

### Meal plan requests (Feature comming soon)

- `make me a healthy meal plan for the week`
- `meal plan`
- `plan my meals low carb`
- `make a high protein meal plan`
