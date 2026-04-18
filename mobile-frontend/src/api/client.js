import axios from "axios";

export const adminApi = axios.create({
  baseURL: "http://localhost:8000/api",
});

export const userApi = axios.create({
  baseURL: "http://localhost:8001/api",
});