"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import QueryForm from "@/components/forms/query-form";

export default function QueryArea() {
  return (
    <Card className="h-[600px] overflow-auto">
      <CardHeader>
        <CardTitle>Search Music</CardTitle>
      </CardHeader>
      <CardContent>
        <QueryForm />
      </CardContent>
    </Card>
  );
}
