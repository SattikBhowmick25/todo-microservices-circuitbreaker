import React, { useState } from "react";

function TodoForm({ onSubmit }) {
    const [formData, setFormData] = useState({
        title: "",
        description: "",
        status: "pending",
    });

    const handleChange = (e) => {
        setFormData((prev) => ({
            ...prev,
            [e.target.name]: e.target.value,
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(formData);
        setFormData({
            title: "",
            description: "",
            status: "pending",
        });
    };

    return (
        <form className="todo-form" onSubmit={handleSubmit}>
            <h2>Create Todo</h2>

            <input
                type="text"
                name="title"
                placeholder="Enter title"
                value={formData.title}
                onChange={handleChange}
                required
            />

            <textarea
                name="description"
                placeholder="Enter description"
                value={formData.description}
                onChange={handleChange}
            />

            <select
                name="status"
                value={formData.status}
                onChange={handleChange}
            >
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
            </select>

            <button type="submit">Add Todo</button>
        </form>
    );
}

export default TodoForm;
