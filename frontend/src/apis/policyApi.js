// src/apis/policyApi.js
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:5001",
  timeout: 20000,
});

// 현재 전체 정책
export const getCurrentPolicies = async () => {
  const { data } = await api.get("/api/policy/current");
  return data; // { status, data: { on_premise, aws: { security_group_rules, ... } } }
};

// 정책 적용 (YAML 업로드)
export const applyNewPolicy = async (formData) => {
  const { data } = await api.post("/api/policy/apply", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data; // { status, message, details... }
};

// 온프레/클라우드 정책 변경 이력 조회
export const getPolicyHistory = async (type = "onprem", range = "daily") => {
  const { data } = await api.get("/api/policy", { params: { type, range } });
  return data; // { status, data: [ {event_name, user, timestamp, details} ] }
};
