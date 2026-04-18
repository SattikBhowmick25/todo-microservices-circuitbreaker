import React from "react";

function TodoTable({ todos, showActions = false, onDelete, onStatusChange }) {
    return (
        <div className="table-wrapper">
            <table className="todo-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Description</th>
                        <th>Status</th>
                        {showActions && <th>Actions</th>}
                    </tr>
                </thead>
                <tbody>
                    {todos.length > 0 ? (
                        todos.map((todo) => (
                            <tr key={todo.id}>
                                <td>{todo.id}</td>
                                <td>{todo.title}</td>
                                <td>{todo.description}</td>
                                <td>
                                    {onStatusChange ? (
                                        <select
                                            value={todo.status}
                                            onChange={(e) =>
                                                onStatusChange(
                                                    todo,
                                                    e.target.value
                                                )
                                            }
                                        >
                                            <option value="pending">
                                                Pending
                                            </option>
                                            <option value="in_progress">
                                                In Progress
                                            </option>
                                            <option value="completed">
                                                Completed
                                            </option>
                                        </select>
                                    ) : (
                                        todo.status
                                    )}
                                </td>
                                {showActions && (
                                    <td>
                                        <button
                                            className="delete-btn"
                                            onClick={() => onDelete(todo.id)}
                                        >
                                            Delete
                                        </button>
                                    </td>
                                )}
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan={showActions ? 5 : 4}>
                                No todos found.
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}

export default TodoTable;
