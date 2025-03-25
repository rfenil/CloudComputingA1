"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { User } from "lucide-react";

const username = "Krish Parekh"

export default function UserArea() {
	const onLogout = () => {};
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
				<div>
					<p className="text-lg font-medium">Welcome, {username}</p>
					<p className="text-sm text-muted-foreground">
						Manage your music subscriptions
					</p>
				</div>
			</CardContent>
		</Card>
	);
}
