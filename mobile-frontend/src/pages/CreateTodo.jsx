import { useState } from "react";
import { adminApi } from "../api/client";
import Header from "../components/Header";

export default function CreateTodo() {
  const [title, setTitle] = useState("");
  const [status, setStatus] = useState("pending");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await adminApi.post("/todos/", { title, status });
      setMessage("Todo created successfully.");
      setTitle("");
      setStatus("pending");
    } catch (error) {
      console.error(error);
      setMessage("Failed to create todo.");
    }
  };

  return (
    <div>
      <Header
        title="Create Todo"
        subtitle="Add a new todo from your phone"
      />

      <form className="card" onSubmit={handleSubmit}>
        <label>Title</label>
        <input
          type="text"
          placeholder="Enter todo title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />

        <label>Status</label>
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
        </select>

        <button className="button" type="submit">
          Create Todo
        </button>

        {message && <p>{message}</p>}
      </form>
    </div>
  );
}