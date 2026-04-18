import { useEffect, useState } from "react";
import { adminApi, userApi } from "../api/client";
import Header from "../components/Header";

export default function Status() {
  const [adminStatus, setAdminStatus] = useState("Checking...");
  const [userStatus, setUserStatus] = useState("Checking...");

  useEffect(() => {
    adminApi.get("/todos/")
      .then(() => setAdminStatus("Admin-write API is reachable"))
      .catch(() => setAdminStatus("Admin-write API is down"));

    userApi.get("/todos/")
      .then(() => setUserStatus("User-status API is reachable"))
      .catch(() => setUserStatus("User-status API is down"));
  }, []);

  return (
    <div>
      <Header
        title="Service Status"
        subtitle="Quick health view for smartphone testing"
      />

      <div className="card">{adminStatus}</div>
      <div className="card">{userStatus}</div>
    </div>
  );
}