import { atom } from "recoil";

const token = localStorage.getItem("token");

export const isAuthenticatedState = atom({
  key: "isAuthenticated",
  default: !!token, // If token exists, default to true; otherwise, false
});
