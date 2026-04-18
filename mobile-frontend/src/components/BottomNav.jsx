import { NavLink } from "react-router-dom";

export default function BottomNav() {
  return (
    <nav className="bottom-nav">
      <NavLink to="/" className={({ isActive }) => isActive ? "active" : ""}>
        Home
      </NavLink>
      <NavLink to="/create" className={({ isActive }) => isActive ? "active" : ""}>
        Create
      </NavLink>
      <NavLink to="/status" className={({ isActive }) => isActive ? "active" : ""}>
        Status
      </NavLink>
    </nav>
  );
}