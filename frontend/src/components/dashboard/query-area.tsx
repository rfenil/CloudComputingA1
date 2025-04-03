"use client";

import QueryForm from "@/components/forms/query-form";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import React from "react";

export default function QueryArea() {
	return (
		<Card className="h-[700px] overflow-auto">
			<CardHeader>
				<CardTitle>Search Music</CardTitle>
			</CardHeader>
			<CardContent>
				<QueryForm />
			</CardContent>
		</Card>
	);
}
