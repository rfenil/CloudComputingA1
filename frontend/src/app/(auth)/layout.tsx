"use client";

import { useRouter } from "next/navigation";
import React from "react";
import { Cookies } from "react-cookie";

interface ILayoutProps {
  children: React.ReactElement;
}

export default function AuthLayout({ children }: ILayoutProps) {
  const user_id = new Cookies().get("user_id");
  const router = useRouter();
  if (user_id) {
    router.replace("/");
  }
  return <>{children}</>;
}
