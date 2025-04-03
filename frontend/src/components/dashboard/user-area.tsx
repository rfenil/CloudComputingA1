"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useBackendQuery } from "@/hooks/useQuery";
import buildURLSearchParams from "@/lib/buildURLSearchParams";
import { cookieOptions } from "@/lib/cookieOptions";
import type { IResponse, IUserResponse } from "@/types/main";
import { User } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useCookies } from "react-cookie";
import { toast } from "sonner";

const URLs = {
	get: "/user",
};

export default function UserArea() {
	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	const [cookies, _setCookie, removeCookie] = useCookies<string>(["user_id"]);
	const router = useRouter();

	const userId = cookies.user_id;

	const { data, isValidating } = useBackendQuery<IResponse<IUserResponse>>(
		`${URLs.get}${buildURLSearchParams({
			user_id: userId,
		})}`,
	);

	const onLogout = () => {
		toast.success("Logout Successful", {
			description: "You have successfully logged out! Redirecting...",
		});
		removeCookie("user_id", cookieOptions);
		router.replace("/login");
	};

	useEffect(() => {
		if (!userId) {
			router.replace("/login");
		}
	}, [userId, router]);

	return (
		<Card>
			<CardHeader className="flex flex-row items-center justify-between pb-2">
				<CardTitle className="text-xl">User Profile</CardTitle>
				<Button variant="ghost" onClick={onLogout}>
					Logout
				</Button>
			</CardHeader>
			<CardContent className="flex items-center space-x-4">
				<div className="bg-primary/10 p-3 rounded-full">
					<User className="h-8 w-8 text-primary" />
				</div>
				<div className="space-y-2">
					{isValidating ? (
						<Skeleton className="w-[200] h-[10px] rounded-full" />
					) : (
						<p className="text-lg font-medium">
							Welcome, {data?.data?.username}
						</p>
					)}

					<p className="text-sm text-muted-foreground">
						Manage your music subscriptions
					</p>
				</div>
			</CardContent>
		</Card>
	);
}
