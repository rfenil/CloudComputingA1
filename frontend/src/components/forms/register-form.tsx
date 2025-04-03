"use client";
import { registerSchema } from "@/components/forms/schema/register-schema";
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
import type { IResponse } from "@/types/main";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import type { z } from "zod";

const URLs = {
	post: "/register",
};

interface IRegisterRequest {
	username: string;
	email: string;
	password: string;
}

interface IRegisterResponse {
	user_id: string;
}

export default function RegisterForm() {
	const router = useRouter();

	const form = useForm<z.infer<typeof registerSchema>>({
		resolver: zodResolver(registerSchema),
		defaultValues: {
			username: "",
			email: "",
			password: "",
		},
	});

	const { trigger, isMutating } = useBackendMutation<
		IRegisterRequest,
		IResponse<IRegisterResponse>
	>(URLs.post, {
		onSuccess() {
			toast.success("Success", {
				description: "Registration successful! Welcome aboard!",
			});
			form.reset();
			router.replace("/login");
		},
		onError(error) {
			toast.error("Error", {
				description: error?.message || "Failed to register. Please try again.",
			});
		},
	});

	const [showPassword, setShowPassword] = useState(false);
	const togglePassword = () => {
		setShowPassword(!showPassword);
	};

	const onSubmit = async (values: z.infer<typeof registerSchema>) => {
		try {
			const registerData = {
				username: values.username,
				email: values.email,
				password: values.password,
			};

			await trigger(registerData);
		} catch {
			toast.error("Error", {
				description: "Unexpected error occured during registration.",
			});
		}
	};

	return (
		<Card className="w-full max-w-lg mx-auto">
			<CardHeader className="space-y-1">
				<CardTitle className="text-2xl">Register</CardTitle>
				<CardDescription>
					Enter your credentials to get started.
				</CardDescription>
			</CardHeader>
			<CardContent>
				<Form {...form}>
					<form onSubmit={form.handleSubmit(onSubmit)}>
						<div className="space-y-4">
							<FormField
								control={form.control}
								name="username"
								render={({ field }) => (
									<FormItem>
										<FormLabel>Username</FormLabel>
										<FormControl>
											<Input type="text" placeholder="john" {...field} />
										</FormControl>
										{form.formState.errors.username && (
											<FormMessage>
												{form.formState.errors.username.message}
											</FormMessage>
										)}
									</FormItem>
								)}
							/>

							<FormField
								control={form.control}
								name="email"
								render={({ field }) => (
									<FormItem>
										<FormLabel>Email</FormLabel>
										<FormControl>
											<Input
												type="email"
												placeholder="s1234567@student.rmit.edu.au"
												{...field}
											/>
										</FormControl>
										{form.formState.errors.email && (
											<FormMessage>
												{form.formState.errors.email.message}
											</FormMessage>
										)}
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
										{form.formState.errors.password && (
											<FormMessage>
												{form.formState.errors.password.message}
											</FormMessage>
										)}
									</FormItem>
								)}
							/>
							<Button className="w-full" type="submit" disabled={isMutating}>
								{isMutating && <Loader2 className="animate-spin" />}
								Register
							</Button>
						</div>
					</form>
				</Form>
			</CardContent>
			<CardFooter className="flex justify-center">
				<p className="text-sm text-center">
					Already have an account?{" "}
					<Link href="/login" className="text-primary underline">
						Login
					</Link>
				</p>
			</CardFooter>
		</Card>
	);
}
