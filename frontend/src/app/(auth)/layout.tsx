"use client";

import { useRouter } from "next/navigation";
import type React from "react";
import { useEffect } from "react";
import { Cookies } from "react-cookie";

interface ILayoutProps {
	children: React.ReactElement;
}

export default function AuthLayout({ children }: ILayoutProps) {
	const router = useRouter();
	useEffect(() => {
		const user_id = new Cookies().get("user_id");
		if (user_id) {
			router.replace("/");
		}
	// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [])
	return <>{children}</>;
}
