"use client";

import QueryArea from "@/components/dashboard/query-area";
import SubscriptionArea from "@/components/dashboard/subscription-area";
import UserArea from "@/components/dashboard/user-area";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Cookies } from "react-cookie";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    const cookies = new Cookies();
    const user_id = cookies.get("user_id");
    if (!user_id) {
      router.replace("/login");
    }
  }, []);
  return (
    <div className="container mx-auto p-4 space-y-8">
      <UserArea />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <SubscriptionArea />
        <QueryArea />
      </div>
    </div>
  );
}


