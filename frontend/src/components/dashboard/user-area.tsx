"use client";

import { useCookies } from "react-cookie";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useBackendQuery } from "@/hooks/useQuery";
import buildURLSearchParams from "@/lib/buildURLSearchParams";
import type { IResponse, IUserResponse } from "@/types/main";
import { User } from "lucide-react";
import { useRouter } from "next/navigation"; 
import { cookieOptions } from "@/lib/cookieOptions";

const URLs = {
  get: "/user",
};

export default function UserArea() {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [cookies, _setCookie, removeCookie] = useCookies<string>(["user_id"]); 
  const router = useRouter(); 

  const userId = cookies.user_id; 

  const { data } = useBackendQuery<IResponse<IUserResponse>>(
    `${URLs.get}${buildURLSearchParams({
      user_id: userId,
    })}`
  );

  const onLogout = () => {
    removeCookie("user_id", cookieOptions); 
    router.push("/login"); 
  };

  if (!userId) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Not Logged In</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Please log in to view your profile.</p>
          <Button onClick={() => router.push("/login")}>Go to Login</Button>
        </CardContent>
      </Card>
    );
  }

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
          <p className="text-lg font-medium">Welcome, {data?.data?.username}</p>
          <p className="text-sm text-muted-foreground">
            Manage your music subscriptions
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
