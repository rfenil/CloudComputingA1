"use client";

import SubscriptionCard from "@/components/subscription-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useBackendQuery } from "@/hooks/useQuery";
import buildURLSearchParams from "@/lib/buildURLSearchParams";
import type { IResponse, MusicItem } from "@/types/main";
/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";
import { useCookies } from "react-cookie";

const URLs = {
	get: "/subscribed",
};

export default function SubscriptionArea() {
	const [cookies, _setCookie, removeCookie] = useCookies<string>(["user_id"]);
	const user_id = cookies.user_id;

	const url = user_id
		? `${URLs.get}${buildURLSearchParams({ user_id })}`
		: null;

	const { data } = useBackendQuery<IResponse<MusicItem[]>>(url);

	return (
		<Card className="h-[700px] overflow-auto">
			<CardHeader>
				<CardTitle>Your Subscriptions</CardTitle>
			</CardHeader>
			<CardContent>
				<div className="space-y-4">
					{data?.data?.map((item) => {
						const key = `${item.artist}#${item.album}#${item.title}`;
						return <SubscriptionCard key={key} item={item} />;
					})}
				</div>
			</CardContent>
		</Card>
	);
}
