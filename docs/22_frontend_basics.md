# 22 — Frontend Basics for Backend Developers (Complete In-Depth Guide)

> 🎯 **Goal**: Backend developer ko frontend samajhna hai - HTML, CSS, JavaScript, API calls!

---

## 📚 Table of Contents
1. [Frontend Kyun Seekhein?](#frontend-kyun-seekhein)
2. [HTML Fundamentals](#html-fundamentals)
3. [CSS Essentials](#css-essentials)
4. [JavaScript Basics](#javascript-basics)
5. [DOM Manipulation](#dom-manipulation)
6. [Fetch API & API Calls](#fetch-api--api-calls)
7. [Forms & Validation](#forms--validation)
8. [Local Storage](#local-storage)
9. [FastAPI Static Files](#fastapi-static-files)
10. [Jinja2 Templates](#jinja2-templates)

---

## Frontend Kyun Seekhein?

### As a Backend Developer

```
Full Stack = Backend + Frontend

Backend Developer ko pata hona chahiye:
1. API responses ko frontend kaise use karega?
2. Form data backend tak kaise aata hai?
3. Authentication token kahan store hota hai?
4. WebSocket connection kaise manage hota hai?

Benefit: Better API design + Better debugging
```

### Frontend Technologies Overview

```
                    Frontend Stack
┌─────────────────────────────────────────────────────┐
│                                                      │
│   HTML (Structure)    ← Page ka skeleton            │
│   CSS (Styling)       ← Colors, layout, fonts       │
│   JavaScript (Logic)  ← Interactivity, API calls    │
│                                                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│   Frameworks (Optional):                            │
│   • React, Vue, Angular, Svelte                     │
│   • Next.js, Nuxt.js (SSR)                         │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## HTML Fundamentals

### Basic Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Metadata (not visible on page) -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My FastAPI App</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- Visible content -->
    <header>
        <h1>Welcome to My App</h1>
    </header>
    
    <main>
        <p>This is the main content.</p>
    </main>
    
    <footer>
        <p>&copy; 2024 My App</p>
    </footer>
    
    <!-- JavaScript at the end (better loading) -->
    <script src="app.js"></script>
</body>
</html>
```

### Common HTML Elements

```html
<!-- Headings -->
<h1>Heading 1 (largest)</h1>
<h2>Heading 2</h2>
<h6>Heading 6 (smallest)</h6>

<!-- Text -->
<p>Paragraph text</p>
<span>Inline text</span>
<strong>Bold text</strong>
<em>Italic text</em>

<!-- Links -->
<a href="https://example.com">Click here</a>
<a href="/about">About page</a>

<!-- Images -->
<img src="photo.jpg" alt="Description of image">

<!-- Lists -->
<ul>  <!-- Unordered (bullets) -->
    <li>Item 1</li>
    <li>Item 2</li>
</ul>

<ol>  <!-- Ordered (numbers) -->
    <li>First</li>
    <li>Second</li>
</ol>

<!-- Containers (no visual, for grouping) -->
<div>Block container</div>
<span>Inline container</span>

<!-- Semantic HTML (better for SEO) -->
<header>Page header</header>
<nav>Navigation</nav>
<main>Main content</main>
<article>Article/blog post</article>
<section>Section of content</section>
<aside>Sidebar</aside>
<footer>Page footer</footer>
```

### Forms (Important for Backend!)

```html
<!-- Form sends data to backend -->
<form action="/api/register" method="POST">
    
    <!-- Text input -->
    <label for="username">Username:</label>
    <input type="text" id="username" name="username" required>
    
    <!-- Email input -->
    <label for="email">Email:</label>
    <input type="email" id="email" name="email" required>
    
    <!-- Password input -->
    <label for="password">Password:</label>
    <input type="password" id="password" name="password" minlength="8">
    
    <!-- Number input -->
    <label for="age">Age:</label>
    <input type="number" id="age" name="age" min="0" max="120">
    
    <!-- Dropdown select -->
    <label for="country">Country:</label>
    <select id="country" name="country">
        <option value="">Select...</option>
        <option value="IN">India</option>
        <option value="US">USA</option>
    </select>
    
    <!-- Radio buttons (one choice) -->
    <label>Gender:</label>
    <input type="radio" name="gender" value="male"> Male
    <input type="radio" name="gender" value="female"> Female
    
    <!-- Checkbox (multiple choices) -->
    <label>Interests:</label>
    <input type="checkbox" name="interests" value="coding"> Coding
    <input type="checkbox" name="interests" value="music"> Music
    
    <!-- Text area -->
    <label for="bio">Bio:</label>
    <textarea id="bio" name="bio" rows="4"></textarea>
    
    <!-- Submit button -->
    <button type="submit">Register</button>
</form>

<!--
Form Submission Methods:
- GET: Data in URL (?username=john&email=...)
- POST: Data in request body (secure for passwords)
-->
```

---

## CSS Essentials

### Three Ways to Add CSS

```html
<!-- 1. Inline (avoid for maintainability) -->
<p style="color: red; font-size: 16px;">Red text</p>

<!-- 2. Internal (in <head>) -->
<style>
    p { color: red; }
</style>

<!-- 3. External (best practice) -->
<link rel="stylesheet" href="styles.css">
```

### CSS Selectors

```css
/* Element selector */
p {
    color: blue;
}

/* Class selector (.) - reusable */
.highlight {
    background-color: yellow;
}
/* HTML: <p class="highlight">Highlighted</p> */

/* ID selector (#) - unique */
#main-title {
    font-size: 24px;
}
/* HTML: <h1 id="main-title">Title</h1> */

/* Multiple classes */
.btn {
    padding: 10px 20px;
}
.btn-primary {
    background: blue;
    color: white;
}
/* HTML: <button class="btn btn-primary">Click</button> */

/* Descendant selector */
.card p {
    color: gray;  /* Only p inside .card */
}

/* Direct child selector */
.nav > li {
    display: inline;  /* Only direct children */
}

/* Pseudo-classes */
a:hover {
    color: red;  /* On mouse hover */
}

button:disabled {
    opacity: 0.5;
}

input:focus {
    border-color: blue;
}
```

### Box Model

```css
/*
Every element is a box:
┌─────────────────────────────────────┐
│             MARGIN                   │ ← Space outside
│   ┌─────────────────────────────┐   │
│   │         BORDER               │   │ ← Border
│   │   ┌─────────────────────┐   │   │
│   │   │      PADDING         │   │   │ ← Space inside
│   │   │   ┌─────────────┐   │   │   │
│   │   │   │   CONTENT    │   │   │   │ ← Actual content
│   │   │   └─────────────┘   │   │   │
│   │   └─────────────────────┘   │   │
│   └─────────────────────────────┘   │
└─────────────────────────────────────┘
*/

.box {
    width: 200px;
    height: 100px;
    padding: 20px;           /* All sides */
    padding: 10px 20px;      /* top-bottom, left-right */
    padding: 10px 20px 15px 25px;  /* top, right, bottom, left */
    margin: 10px;
    border: 2px solid black;
    
    /* Include padding/border in width */
    box-sizing: border-box;  /* Always use this! */
}
```

### Flexbox (Layout)

```css
/*
Flexbox = Easy way to layout items

┌────────────────────────────────────────┐
│  ┌────┐  ┌────┐  ┌────┐  ┌────┐       │
│  │ 1  │  │ 2  │  │ 3  │  │ 4  │       │
│  └────┘  └────┘  └────┘  └────┘       │
└────────────────────────────────────────┘
*/

.container {
    display: flex;
    
    /* Main axis direction */
    flex-direction: row;     /* horizontal (default) */
    flex-direction: column;  /* vertical */
    
    /* Align on main axis */
    justify-content: flex-start;   /* start */
    justify-content: center;       /* center */
    justify-content: flex-end;     /* end */
    justify-content: space-between; /* spread out */
    justify-content: space-around;  /* space around */
    
    /* Align on cross axis */
    align-items: flex-start;
    align-items: center;
    align-items: flex-end;
    
    /* Wrap items */
    flex-wrap: wrap;
    
    /* Gap between items */
    gap: 20px;
}

.item {
    flex: 1;  /* Take equal space */
    flex: 2;  /* Take 2x space */
}
```

### Responsive Design

```css
/* Mobile-first approach */

/* Default (mobile) */
.container {
    width: 100%;
    padding: 10px;
}

/* Tablet and up */
@media (min-width: 768px) {
    .container {
        width: 750px;
        margin: 0 auto;
    }
}

/* Desktop and up */
@media (min-width: 1024px) {
    .container {
        width: 1000px;
    }
}

/* Hide on mobile */
.desktop-only {
    display: none;
}

@media (min-width: 768px) {
    .desktop-only {
        display: block;
    }
}
```

---

## JavaScript Basics

### Variables

```javascript
// let - can be changed
let count = 0;
count = 5;

// const - cannot be reassigned
const API_URL = "http://localhost:8000";

// var - old way, avoid it
var oldWay = "don't use";

// Data types
let name = "John";           // String
let age = 25;                // Number
let isActive = true;         // Boolean
let nothing = null;          // Null
let notDefined;              // Undefined
let user = { name: "John" }; // Object
let items = [1, 2, 3];       // Array
```

### Functions

```javascript
// Traditional function
function greet(name) {
    return "Hello, " + name;
}

// Arrow function (preferred)
const greet = (name) => {
    return "Hello, " + name;
};

// Short arrow function
const greet = (name) => "Hello, " + name;

// Async function (for API calls)
const fetchUser = async (userId) => {
    const response = await fetch(`/api/users/${userId}`);
    return await response.json();
};
```

### Objects & Arrays

```javascript
// Object (like Python dict)
const user = {
    id: 1,
    name: "John",
    email: "john@example.com",
    isAdmin: false
};

// Access properties
user.name;          // "John"
user["email"];      // "john@example.com"

// Destructuring
const { name, email } = user;


// Array (like Python list)
const numbers = [1, 2, 3, 4, 5];

// Array methods
numbers.push(6);              // Add to end
numbers.pop();                // Remove from end
numbers.length;               // 5

// Iteration
numbers.forEach(num => console.log(num));

// Map (transform each item)
const doubled = numbers.map(num => num * 2);
// [2, 4, 6, 8, 10]

// Filter
const evens = numbers.filter(num => num % 2 === 0);
// [2, 4]

// Find
const found = numbers.find(num => num > 3);
// 4

// Spread operator
const moreNumbers = [...numbers, 6, 7, 8];
```

### Template Literals

```javascript
const name = "John";
const age = 25;

// Old way
const message = "Hello, " + name + "! You are " + age + " years old.";

// Template literal (use backticks)
const message = `Hello, ${name}! You are ${age} years old.`;

// Multi-line strings
const html = `
    <div class="card">
        <h2>${name}</h2>
        <p>Age: ${age}</p>
    </div>
`;
```

---

## DOM Manipulation

### Selecting Elements

```javascript
// By ID
const header = document.getElementById("header");

// By class (returns array-like)
const cards = document.getElementsByClassName("card");

// Query selector (CSS selector)
const firstCard = document.querySelector(".card");  // First match
const allCards = document.querySelectorAll(".card");  // All matches

// By tag
const paragraphs = document.getElementsByTagName("p");
```

### Modifying Elements

```javascript
// Get element
const title = document.getElementById("title");

// Change text
title.textContent = "New Title";

// Change HTML
title.innerHTML = "<span>New Title</span>";

// Change styles
title.style.color = "red";
title.style.fontSize = "24px";

// Add/remove classes
title.classList.add("highlight");
title.classList.remove("old-class");
title.classList.toggle("active");  // Add if missing, remove if present

// Attributes
const link = document.querySelector("a");
link.setAttribute("href", "https://new-url.com");
link.getAttribute("href");
link.removeAttribute("target");
```

### Creating Elements

```javascript
// Create element
const newCard = document.createElement("div");
newCard.className = "card";
newCard.innerHTML = `
    <h3>New Card</h3>
    <p>Card content</p>
`;

// Add to DOM
document.getElementById("container").appendChild(newCard);

// Insert before another element
const container = document.getElementById("container");
const firstChild = container.firstChild;
container.insertBefore(newCard, firstChild);

// Remove element
newCard.remove();
```

### Event Handling

```javascript
// Click event
const button = document.getElementById("submit-btn");

button.addEventListener("click", (event) => {
    console.log("Button clicked!");
    event.preventDefault();  // Prevent default action (form submit, link follow)
});

// Form submit
const form = document.getElementById("login-form");

form.addEventListener("submit", async (event) => {
    event.preventDefault();  // Prevent page reload
    
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Send to API
    const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
});

// Input change
const input = document.getElementById("search");

input.addEventListener("input", (event) => {
    console.log("User typed:", event.target.value);
});

// Keyboard events
document.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        console.log("Enter pressed");
    }
});
```

---

## Fetch API & API Calls

### GET Request

```javascript
// Simple GET
const response = await fetch("/api/users");
const users = await response.json();
console.log(users);


// GET with query parameters
const searchTerm = "john";
const response = await fetch(`/api/users?search=${searchTerm}`);


// GET with error handling
async function getUsers() {
    try {
        const response = await fetch("/api/users");
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const users = await response.json();
        return users;
        
    } catch (error) {
        console.error("Error fetching users:", error);
        throw error;
    }
}
```

### POST Request

```javascript
async function createUser(userData) {
    const response = await fetch("/api/users", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail);
    }
    
    return await response.json();
}

// Usage
const newUser = await createUser({
    name: "John",
    email: "john@example.com",
    password: "secret123"
});
```

### PUT/PATCH/DELETE

```javascript
// PUT (full update)
await fetch(`/api/users/${userId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(fullUserData),
});


// PATCH (partial update)
await fetch(`/api/users/${userId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: "New Name" }),
});


// DELETE
await fetch(`/api/users/${userId}`, {
    method: "DELETE",
});
```

### With Authentication

```javascript
// Get token from storage
const token = localStorage.getItem("access_token");

// Include in request
const response = await fetch("/api/protected", {
    headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
    },
});


// Reusable fetch wrapper
async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem("access_token");
    
    const defaultHeaders = {
        "Content-Type": "application/json",
    };
    
    if (token) {
        defaultHeaders["Authorization"] = `Bearer ${token}`;
    }
    
    const response = await fetch(endpoint, {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    });
    
    if (response.status === 401) {
        // Token expired, redirect to login
        window.location.href = "/login";
        return;
    }
    
    return response;
}

// Usage
const response = await apiFetch("/api/users");
const users = await response.json();
```

---

## Forms & Validation

### Client-Side Validation

```html
<form id="register-form">
    <input 
        type="email" 
        name="email" 
        required 
        pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"
    >
    
    <input 
        type="password" 
        name="password" 
        required 
        minlength="8"
    >
    
    <button type="submit">Register</button>
</form>
```

```javascript
const form = document.getElementById("register-form");

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    
    const formData = new FormData(form);
    const email = formData.get("email");
    const password = formData.get("password");
    
    // Custom validation
    const errors = [];
    
    if (!email.includes("@")) {
        errors.push("Invalid email format");
    }
    
    if (password.length < 8) {
        errors.push("Password must be at least 8 characters");
    }
    
    if (!/[A-Z]/.test(password)) {
        errors.push("Password must contain uppercase letter");
    }
    
    if (errors.length > 0) {
        displayErrors(errors);
        return;
    }
    
    // Submit to API
    try {
        const response = await fetch("/api/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });
        
        if (!response.ok) {
            const data = await response.json();
            displayErrors([data.detail]);
            return;
        }
        
        // Success
        window.location.href = "/login";
        
    } catch (error) {
        displayErrors(["Network error. Please try again."]);
    }
});

function displayErrors(errors) {
    const errorDiv = document.getElementById("errors");
    errorDiv.innerHTML = errors.map(e => `<p class="error">${e}</p>`).join("");
}
```

---

## Local Storage

### Storing Data

```javascript
// Store string
localStorage.setItem("username", "john");

// Store object (must convert to string)
const user = { id: 1, name: "John" };
localStorage.setItem("user", JSON.stringify(user));

// Store token
localStorage.setItem("access_token", "eyJhbGciOiJIUzI1NiIs...");
```

### Retrieving Data

```javascript
// Get string
const username = localStorage.getItem("username");

// Get object
const user = JSON.parse(localStorage.getItem("user"));

// Get with default
const theme = localStorage.getItem("theme") || "light";
```

### Remove Data

```javascript
// Remove specific item
localStorage.removeItem("access_token");

// Clear all
localStorage.clear();
```

### Session Storage

```javascript
// Same API, but data cleared when browser closes
sessionStorage.setItem("temp_data", "value");
sessionStorage.getItem("temp_data");
sessionStorage.removeItem("temp_data");
```

---

## FastAPI Static Files

### Serving Static Files

```python
# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Now files in static/ folder are available at /static/...
# static/styles.css → http://localhost:8000/static/styles.css
# static/app.js → http://localhost:8000/static/app.js
```

### Project Structure

```
project/
├── main.py
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── app.js
│   └── images/
│       └── logo.png
└── templates/
    └── index.html
```

---

## Jinja2 Templates

### Setup

```python
# pip install jinja2

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "My App",
            "user": {"name": "John", "email": "john@example.com"}
        }
    )
```

### Template Syntax

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <!-- Variables -->
    <h1>Hello, {{ user.name }}!</h1>
    
    <!-- Conditionals -->
    {% if user %}
        <p>Logged in as {{ user.email }}</p>
    {% else %}
        <p>Please log in</p>
    {% endif %}
    
    <!-- Loops -->
    <ul>
    {% for item in items %}
        <li>{{ item.name }} - ${{ item.price }}</li>
    {% endfor %}
    </ul>
    
    <!-- Filters -->
    <p>{{ user.name | upper }}</p>  <!-- JOHN -->
    <p>{{ price | round(2) }}</p>   <!-- 99.99 -->
    
    <!-- Include other templates -->
    {% include "partials/header.html" %}
    
    <!-- Template inheritance -->
    {% extends "base.html" %}
    {% block content %}
        <p>Page specific content</p>
    {% endblock %}
</body>
</html>
```

### Base Template

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My App{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <nav>
        {% include "partials/navbar.html" %}
    </nav>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <p>&copy; 2024 My App</p>
    </footer>
    
    <script src="/static/js/app.js"></script>
</body>
</html>


<!-- templates/home.html -->
{% extends "base.html" %}

{% block title %}Home - My App{% endblock %}

{% block content %}
<h1>Welcome!</h1>
<p>This is the home page.</p>
{% endblock %}
```

---

## Quick Reference

```javascript
// DOM Selection
document.getElementById("id");
document.querySelector(".class");
document.querySelectorAll("tag");

// DOM Modification
element.textContent = "text";
element.innerHTML = "<p>HTML</p>";
element.classList.add("class");

// Events
element.addEventListener("click", (e) => {});

// Fetch API
await fetch(url);
await fetch(url, { method: "POST", body: JSON.stringify(data) });

// Local Storage
localStorage.setItem("key", "value");
localStorage.getItem("key");
localStorage.removeItem("key");
```

---

> **Pro Tip**: "Frontend samajhne se tum better APIs design karoge - kyunki pata hoga ki frontend developer ko kya chahiye!" 🎨
