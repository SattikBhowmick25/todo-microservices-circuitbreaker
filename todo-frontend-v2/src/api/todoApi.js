const ADMIN_BASE_URL = "http://localhost:8000/api/todos/";
const USER_BASE_URL = "http://localhost:8001/api/todos/";

export async function getAdminTodos() {
    const response = await fetch(ADMIN_BASE_URL);
    if (!response.ok) {
        throw new Error("Failed to fetch admin todos");
    }
    return response.json();
}

export async function createAdminTodo(todoData) {
    const response = await fetch(ADMIN_BASE_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(todoData),
    });

    if (!response.ok) {
        throw new Error("Failed to create todo");
    }

    return response.json();
}

export async function updateAdminTodo(id, todoData) {
    const response = await fetch(`${ADMIN_BASE_URL}${id}/`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(todoData),
    });

    if (!response.ok) {
        throw new Error("Failed to update admin todo");
    }

    return response.json();
}

export async function deleteAdminTodo(id) {
    const response = await fetch(`${ADMIN_BASE_URL}${id}/`, {
        method: "DELETE",
    });

    if (!response.ok) {
        throw new Error("Failed to delete admin todo");
    }

    return true;
}

export async function getUserTodos() {
    const response = await fetch(USER_BASE_URL);
    if (!response.ok) {
        throw new Error("Failed to fetch user todos");
    }
    return response.json();
}

export async function updateUserTodo(id, todoData) {
    const response = await fetch(`${USER_BASE_URL}${id}/`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(todoData),
    });

    if (!response.ok) {
        throw new Error("Failed to update user todo");
    }

    return response.json();
}
