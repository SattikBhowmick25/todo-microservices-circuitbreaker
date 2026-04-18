import React from "react";
import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

function Layout() {
    return (
        <div>
            <Navbar />
            <main className="main-container">
                <Outlet />
            </main>
        </div>
    );
}

export default Layout;
