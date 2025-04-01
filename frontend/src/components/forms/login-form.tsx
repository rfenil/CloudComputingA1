"use client";

import { loginSchema } from "@/components/forms/schema/login-schema";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardFooter,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import {
	Form,
	FormControl,
	FormField,
	FormItem,
	FormLabel,
	FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useBackendMutation } from "@/hooks/useMutations";
import { cookieOptions } from "@/lib/cookieOptions";
import type { ILoginRequest, ILoginResponse } from "@/types/auth";
import type { IResponse } from "@/types/main";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useState } from "react";
import { useCookies } from "react-cookie";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import type { z } from "zod";

const URLs = {
	post: "/login",
};

export default function LoginForm() {

	const router = useRouter();

	const setCookie = useCookies<string>([])[1];
	const { trigger, isMutating } = useBackendMutation<
		ILoginRequest,
		IResponse<ILoginResponse>
	>(URLs.post, {
		onSuccess(data) {
			toast.success("Login Successful", {
				description: "You have successfully logged in! Redirecting...",
			});
			setCookie("user_id", data?.data?.user_id, { ...cookieOptions });
			router.push("/")
			form.reset();
		},
		onError(error) {
			toast.error("Login Failed", {
				description: error?.message || "Invalid credentials. Please try again.",
			});
		},
	});

	const form = useForm<z.infer<typeof loginSchema>>({
		resolver: zodResolver(loginSchema),
		defaultValues: {
			email: "",
			password: "",
		},
	});

	const [showPassword, setShowPassword] = useState(false);
	const togglePassword = () => setShowPassword((prev) => !prev);

	const onSubmit = async (data: z.infer<typeof loginSchema>) => {
		await trigger({ email: data.email, password: data.password });
	};

	return (
		<Card className="w-full max-w-lg mx-auto">
			<CardHeader className="space-y-1">
				<CardTitle className="text-2xl">Login</CardTitle>
				<CardDescription>Enter your credentials to continue.</CardDescription>
			</CardHeader>
			<CardContent>
				<Form {...form}>
					<form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
						<FormField
							control={form.control}
							name="email"
							render={({ field }) => (
								<FormItem>
									<FormLabel>Email</FormLabel>
									<FormControl>
										<Input
											type="email"
											placeholder="your.email@example.com"
											{...field}
										/>
									</FormControl>
									<FormMessage />
								</FormItem>
							)}
						/>

						<FormField
							control={form.control}
							name="password"
							render={({ field }) => (
								<FormItem>
									<FormLabel>Password</FormLabel>
									<FormControl>
										<div className="relative">
											<Input
												type={showPassword ? "text" : "password"}
												placeholder="••••••••"
												{...field}
											/>
											<Button
												type="button"
												variant="ghost"
												size="icon"
												className="absolute right-0 top-0 h-full px-3"
												onClick={togglePassword}
											>
												{showPassword ? (
													<EyeOff className="h-4 w-4" />
												) : (
													<Eye className="h-4 w-4" />
												)}
												<span className="sr-only">
													{showPassword ? "Hide password" : "Show password"}
												</span>
											</Button>
										</div>
									</FormControl>
									<FormMessage />
								</FormItem>
							)}
						/>

						<Button className="w-full" type="submit" disabled={isMutating}>
							{isMutating && <Loader2 className="animate-spin" />}
							Login
						</Button>
					</form>
				</Form>
			</CardContent>
			<CardFooter className="flex justify-center">
				<p className="text-sm text-center">
					Don&apos;t have an account?{" "}
					<Link href="/register" className="text-primary underline">
						Sign up
					</Link>
				</p>
			</CardFooter>
		</Card>
	);
}
