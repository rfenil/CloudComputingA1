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
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff } from "lucide-react";
import Link from "next/link";
import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import type { z } from "zod";

export default function RegisterForm() {
	const form = useForm<z.infer<typeof registerSchema>>({
		resolver: zodResolver(registerSchema),
		defaultValues: {
			first_name: "",
			last_name: "",
			email: "",
			password: "",
		},
	});

	const [showPassword, setShowPassword] = useState(false);
	const togglePassword = () => {
		setShowPassword(!showPassword);
	};

	const onSubmit = (values: z.infer<typeof registerSchema>) => {
		console.log(values);
		toast.success("Success", {
			description: "Registration successful!",
		});
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
							<div className="flex gap-x-4">
								<FormField
									control={form.control}
									name="first_name"
									render={({ field }) => (
										<FormItem>
											<FormLabel>First Name</FormLabel>
											<FormControl>
												<Input type="text" placeholder="john" {...field} />
											</FormControl>
											{form.formState.errors.first_name && (
												<FormMessage>
													{form.formState.errors.first_name.message}
												</FormMessage>
											)}
										</FormItem>
									)}
								/>
								<FormField
									control={form.control}
									name="last_name"
									render={({ field }) => (
										<FormItem>
											<FormLabel>Last Name</FormLabel>
											<FormControl>
												<Input type="text" placeholder="doe" {...field} />
											</FormControl>
											{form.formState.errors.last_name && (
												<FormMessage>
													{form.formState.errors.last_name.message}
												</FormMessage>
											)}
										</FormItem>
									)}
								/>
							</div>
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
							<Button className="w-full" type="submit">
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
