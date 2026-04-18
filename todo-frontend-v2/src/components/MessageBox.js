import React from "react";

function MessageBox({ type = "info", message }) {
    if (!message) return null;

    return <div className={`message-box ${type}`}>{message}</div>;
}

export default MessageBox;
