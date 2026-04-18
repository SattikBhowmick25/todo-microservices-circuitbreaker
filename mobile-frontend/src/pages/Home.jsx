import { useEffect, useState } from "react";
import { userApi } from "../api/client";
import Header from "../components/Header";
import TodoCard from "../components/TodoCard";
import EmptyState from "../components/EmptyState";

export default function Home() {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    userApi.get("/todos/")
      .then((res) => setTodos(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <Header
        title="My Todos"
        subtitle="Phone-first view for your microservices todo app"
      />

      {loading ? (
        <EmptyState message="Loading todos..." />
      ) : todos.length === 0 ? (
        <EmptyState message="No todos found." />
      ) : (
        todos.map((todo) => <TodoCard key={todo.id} todo={todo} />)
      )}
    </div>
  );
}