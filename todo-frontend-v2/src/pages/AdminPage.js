import React, { useEffect, useState } from "react";
import TodoForm from "../components/TodoForm";
import TodoTable from "../components/TodoTable";
import MessageBox from "../components/MessageBox";
import {
    getAdminTodos,
    createAdminTodo,
    deleteAdminTodo,
} from "../api/todoApi";

function AdminPage() {
    const [todos, setTodos] = useState([]);
    const [message, setMessage] = useState("");
    const [messageType, setMessageType] = useState("info");

    const loadTodos = async () => {
        try {
            const data = await getAdminTodos();
            setTodos(data);
        } catch (error) {
            setMessage("Unable to load admin todos.");
            setMessageType("error");
        }
    };

    useEffect(() => {
        loadTodos();
    }, []);

    const handleCreate = async (formData) => {
        try {
            await createAdminTodo(formData);
            setMessage("Todo created successfully.");
            setMessageType("success");
            loadTodos();
        } catch (error) {
            setMessage("Failed to create todo.");
            setMessageType("error");
        }
    };

    const handleDelete = async (id) => {
        try {
            await deleteAdminTodo(id);
            setMessage("Todo deleted successfully.");
            setMessageType("success");
            loadTodos();
        } catch (error) {
            setMessage("Failed to delete todo.");
            setMessageType("error");
        }
    };

    return (
        <div className="page-card">
            <h1>Admin Page</h1>
            <p>
                This page connects to the admin-write service and is used for
                creating and managing todos.
            </p>

            <MessageBox type={messageType} message={message} />

            <TodoForm onSubmit={handleCreate} />

            <h2 className="section-title">Admin Todos</h2>
            <TodoTable
                todos={todos}
                showActions={true}
                onDelete={handleDelete}
            />
        </div>
    );
}

export default AdminPage;
