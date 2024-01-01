// src/components/Flight.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Flight = () => {
  const [flights, setFlights] = useState([]);

  useEffect(() => {
    // Fetch flights from Django backend
    axios.get('http://localhost:8000/flight/')
      .then(response => setFlights(response.data))
      .catch(error => console.error(error));
  }, []);

  return (
    <div>
      <h1>Flight Data</h1>
      <ul>
        {flights.map((flight, index) => (
          <li key={index}>
            {flight.dep_arrival_times} - {flight.airlines} - {flight.prices}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Flight;
