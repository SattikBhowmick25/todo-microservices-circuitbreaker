import React, { useEffect, useState } from "react";
import TodoTable from "../components/TodoTable";
import MessageBox from "../components/MessageBox";
import { getUserTodos, updateUserTodo } from "../api/todoApi";

function UserPage() {
  const [todos, setTodos] = useState([]);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("info");

  const loadTodos = async () => {
    try {
      const data = await getUserTodos();
      setTodos(data);
    } catch (error) {
      setMessage("Unable to load user todos.");
      setMessageType("error");
    }
  };

  useEffect(() => {
    loadTodos();
  }, []);

  const handleStatusChange = async (todo, newStatus) => {
    try {
      const updatedTodo = {
        ...todo,
        status: newStatus,
      };
      await updateUserTodo(todo.id, updatedTodo);
      setMessage("Todo status updated successfully.");
      setMessageType("success");
      loadTodos();
    } catch (error) {
      setMessage("Failed to update todo status.");
      setMessageType("error");
    }
  };

  return (
    <div className="page-card">
      <h1>User Page</h1>
      <p>
        This page connects to the user-status service and displays synchronized
        todos received through RabbitMQ.
      </p>

      <MessageBox type={messageType} message={message} />

      <h2 className="section-title">User Todos</h2>
      <TodoTable todos={todos} onStatusChange={handleStatusChange} />
    </div>
  );
}

export default UserPage;