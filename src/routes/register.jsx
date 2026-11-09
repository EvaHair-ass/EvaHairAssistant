import { createFileRoute } from "@tanstack/react-router";
import { RegisterPage } from "@/components/auth/RegisterPage";

export const Route = createFileRoute("/register")({ ssr: false, head: () => ({ meta: [{ title: "Регистрация — Цифровые сотрудники" }] }), component: RegisterPage });