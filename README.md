# 🍳 Chefbot

## Prerequisites

Before running the project, make sure you have the following installed:

- Python 3.10+
- Node.js 18+ 
- Flask and Flask-CORS Python packages  

--- 

## How to run

### Recommended (All platforms)

From project root (/ChefBot), run:

```
python start.py
```
This will start Flask backend on port 5000 and Vite frontend on port 5173 

When you see something like:
```
 VITE v5.4.21  ready in 227 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```
Type 'o' in terminal and press enter or open URL in browser to use ChefBot.

When you're done
- close website
- Go back to the same terminal, click on it, and press ctrl+c once

### Second Method (sets up both ports at the same time)
Enter 
```
./setup.sh
chmod +x start.sh
./ start.sh
```

If it says that ports could not be be set public, manually change port visibility of ports 5000 and 5173 to public


### Manually (Two terminals)

To start create 2 terminals that happen in the frontend and backend (cd to respective folders once you open terminal)

Also create port 5000 and set its visibility to public (will find a fix on this later)
Make sure that the backendURL in app.jsx (frontend) matches with the current port local address (will find a permanent fix later but i had to input it manually since i was using github Codespaces)


### Terminal 1 (backend)
Enter following commands

```
cd backend
python app.py  
```
This command starts the Flask backend server.  
You should then see something like. 
```
* Serving Flask app 'app'
* Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 ```

If you see any minor warnings or errors, you can ignore them for now — they’ll be addressed later.


###  Terminal 2 (frontend)
Enter following commands

```
cd frontend
npm run dev
```

This command starts the React (Vite) frontend. You should see something like 

```
 VITE v5.4.21  ready in 227 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help

```
Once both servers are running, open your browser and visit http://localhost:5173 to use the chatbot.


