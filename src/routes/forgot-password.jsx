import { createFileRoute } from "@tanstack/react-router";
import { ForgotPasswordPage } from "@/components/auth/ForgotPasswordPage";

export const Route = createFileRoute("/forgot-password")({ ssr: false, head: () => ({ meta: [{ title: "Восстановление пароля — Цифровые сотрудники" }] }), component: ForgotPasswordPage });