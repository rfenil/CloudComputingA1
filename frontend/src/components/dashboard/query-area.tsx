"use client";

import SearchContainer from "@/components/search-container";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import React from "react";

export default function QueryArea() {
	return (
		<Card className="h-[700px] overflow-auto">
			<CardHeader>
				<CardTitle>Search Music</CardTitle>
			</CardHeader>
			<CardContent>
				<SearchContainer />
			</CardContent>
		</Card>
	);
}
