"use client";

import { redirect } from "next/navigation";
import { type ReactNode, useLayoutEffect } from "react";
import { useCookies } from "react-cookie";

interface ITemplateProps {
	children: ReactNode;
}

export default function Template({ children }: ITemplateProps) {
	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	const [cookies, _setCookie, removeCookie] = useCookies<string>(["user_id"]);
	const userId = cookies.user_id;

	useLayoutEffect(() => {
		if (userId === "") {
			redirect("/login");
		}
	}, [userId]);

	return children;
}
