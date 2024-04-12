// Filename - App.js

// Importing modules
import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  // usestate for setting a javascript
  // object for storing and using data
  const [data, setdata] = useState({
    name: "",
    age: 0,
    date: "",
    programming: "",
  });

  // Using useEffect for single rendering
  useEffect(() => {
    // Using fetch to fetch the api from 
    // flask server it will be redirected to proxy
    fetch("http://localhost:5000/data").then((res) =>
      res.json().then((data) => {
        // Setting a data from api
        setdata({
          name: data.Name,
          age: data.Age,
          date: data.Date,
          programming: data.programming,
        });
      })
    );
  }, []);

  return (
    <div className="App">
      <div class="board">
        <form id="todo-form">
          <input type="text" placeholder="New TODO..." id="todo-input" />
          <button type="submit">Add +</button>
        </form>

        <div class="lanes">
          <div class="swim-lane" id="todo-lane">
            <h3 class="heading">TODO</h3>

            <p class="task" draggable="true">Get groceries</p>
            <p class="task" draggable="true">Feed the dogs</p>
            <p class="task" draggable="true">Mow the lawn</p>
          </div>

          <div class="swim-lane">
            <h3 class="heading">Doing</h3>

            <p class="task" draggable="true">Binge 80 hours of Game of Thrones</p>
          </div>

          <div class="swim-lane">
            <h3 class="heading">Done</h3>

            <p class="task" draggable="true">
              Watch video of a man raising a grocery store lobster as a pet
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
