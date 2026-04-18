import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import CreateTodo from "./pages/CreateTodo";
import Status from "./pages/Status";
import BottomNav from "./components/BottomNav";

export default function App() {
    return (
        <div className="app-shell">
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/create" element={<CreateTodo />} />
                <Route path="/status" element={<Status />} />
            </Routes>
            <BottomNav />
        </div>
    );
}
