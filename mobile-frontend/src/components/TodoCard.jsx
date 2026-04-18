export default function TodoCard({ todo }) {
  return (
    <div className="card">
      <div className="todo-title">{todo.title}</div>
      <div className="todo-meta">ID: {todo.id}</div>
      <div className="todo-meta">Status: {todo.status}</div>
      <div className="status-pill">{todo.status}</div>
    </div>
  );
}