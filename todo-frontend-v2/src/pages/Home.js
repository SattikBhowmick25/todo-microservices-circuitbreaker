import React from "react";

function Home() {
  return (
    <div className="page-card">
      <h1>Todo Microservices Version 2.0</h1>
      <p>
        This frontend is designed for the RabbitMQ-based microservices version
        of the todo project.
      </p>
      <p>
        Use the Admin page to manage todo creation and deletion, and use the
        User page to view synchronized todos and update status.
      </p>
    </div>
  );
}

export default Home;