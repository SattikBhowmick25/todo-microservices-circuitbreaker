import React from "react";
import { NavLink } from "react-router-dom";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="logo">Todo Microservices V2</div>
      <div className="nav-links">
        <NavLink to="/" className="nav-link">
          Home
        </NavLink>
        <NavLink to="/admin" className="nav-link">
          Admin Page
        </NavLink>
        <NavLink to="/user" className="nav-link">
          User Page
        </NavLink>
      </div>
    </nav>
  );
}

export default Navbar;