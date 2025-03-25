"use client";
import { musicSearchSchema } from "@/components/forms/schema/query-schema";
import { Button } from "@/components/ui/button";
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
import { Search } from "lucide-react";
import React from "react";
import { useForm } from "react-hook-form";
import type { z } from "zod";

export default function QueryForm() {
	const form = useForm<z.infer<typeof musicSearchSchema>>({
		resolver: zodResolver(musicSearchSchema),
		defaultValues: {
			title: "",
			artist: "",
			album: "",
			year: "",
		},
	});

	const onSubmit = (values: z.infer<typeof musicSearchSchema>) => {
		console.log(values);
	};

	return (
		<Form {...form}>
			<form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
				<div className="grid grid-cols-2 gap-4">
					<FormField
						control={form.control}
						name="title"
						render={({ field }) => (
							<FormItem className="space-y-2">
								<FormLabel htmlFor="title">Title</FormLabel>
								<FormControl>
									<Input id="title" placeholder="Song title" {...field} />
								</FormControl>
								<FormMessage />
							</FormItem>
						)}
					/>
					<FormField
						control={form.control}
						name="artist"
						render={({ field }) => (
							<FormItem className="space-y-2">
								<FormLabel htmlFor="artist">Artist</FormLabel>
								<FormControl>
									<Input id="artist" placeholder="Artist name" {...field} />
								</FormControl>
								<FormMessage />
							</FormItem>
						)}
					/>
					<FormField
						control={form.control}
						name="album"
						render={({ field }) => (
							<FormItem className="space-y-2">
								<FormLabel htmlFor="album">Album</FormLabel>
								<FormControl>
									<Input id="album" placeholder="Album name" {...field} />
								</FormControl>
								<FormMessage />
							</FormItem>
						)}
					/>
					<FormField
						control={form.control}
						name="year"
						render={({ field }) => (
							<FormItem className="space-y-2">
								<FormLabel htmlFor="year">Year</FormLabel>
								<FormControl>
									<Input id="year" placeholder="Release year" {...field} />
								</FormControl>
								<FormMessage />
							</FormItem>
						)}
					/>
				</div>
				<Button type="submit" className="w-full">
					Query
					<Search className="ml-2 h-4 w-4" />
				</Button>
			</form>
		</Form>
	);
}
