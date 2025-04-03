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
import {
	Pagination,
	PaginationContent,
	PaginationItem,
	PaginationNext,
	PaginationPrevious,
} from "@/components/ui/pagination";
import { useBackendMutation } from "@/hooks/useMutations";
import { useBackendQuery } from "@/hooks/useQuery";
import buildURLSearchParams from "@/lib/buildURLSearchParams";
import revalidate from "@/lib/revalidate";
import type { MusicItem } from "@/types/main";
import { zodResolver } from "@hookform/resolvers/zod";
import { Music, Search } from "lucide-react";
import Image from "next/image";
import React, { useState } from "react";
import { useCookies } from "react-cookie";
import { useForm } from "react-hook-form";
import { mutate } from "swr";
import type { z } from "zod";

interface IQueryForm {
	data: {
		Items: MusicItem[];
	};
}

export default function QueryForm() {
	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	const [cookies, _setCookie, removeCookie] = useCookies<string>(["user_id"]);
	const userId = cookies.user_id;
	const [queryParams, setQueryParams] = useState("");
	const [page, setPage] = useState(1);
	const pageSize = 2;
	const { data, isLoading } = useBackendQuery<IQueryForm>(
		queryParams !== "" ? `/search?${queryParams}` : null,
		{
			onSuccess(data) {
				revalidate(
					`/subscribed${buildURLSearchParams({
						user_id: userId,
					})}`,
				);
			},
		},
	);
	const { trigger } = useBackendMutation("/subscribe");

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
		const filteredValues = Object.fromEntries(
			Object.entries(values).filter(([_, value]) => value !== ""),
		);

		if (Object.keys(filteredValues).length === 0) return;

		const params = new URLSearchParams(
			filteredValues as Record<string, string>,
		).toString();
		setQueryParams(params);
		setPage(1);
	};

	const onSubscribe = async (music: MusicItem) => {
		await trigger({
			user_id: userId,
			artist: music.artist,
			year: music.year,
			title: music.title,
			album: music.album,
			img_url: music.img_url,
		});
	};
	const paginatedData =
		data?.data?.Items?.slice((page - 1) * pageSize, page * pageSize) || [];
	console.log(paginatedData);
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
			{paginatedData.length > 0 && (
				<div className="mt-6 space-y-4">
					{paginatedData.map((item, index) => (
						<div
							key={item.id}
							className="border rounded-lg p-4 flex flex-col sm:flex-row gap-4"
						>
							<div className="relative w-24 h-24 flex-shrink-0 mx-auto sm:mx-0">
								{item.img_url ? (
									<Image
										src={item.img_url || "/placeholder.svg"}
										alt={`${item.artist} image`}
										fill
										className="object-cover rounded-md"
									/>
								) : (
									<div className="w-full h-full bg-muted flex items-center justify-center rounded-md">
										<Music className="h-8 w-8 text-muted-foreground" />
									</div>
								)}
							</div>
							<div className="flex-1 space-y-2">
								<h3 className="font-medium">{item.title}</h3>
								<div className="text-sm text-muted-foreground">
									<p>Artist: {item.artist}</p>
									<p>Album: {item.album}</p>
									<p>Year: {item.year}</p>
								</div>
								<Button
									variant="secondary"
									size="sm"
									onClick={() => {
										onSubscribe(item);
									}}
								>
									Subscribe
								</Button>
							</div>
						</div>
					))}
					<Pagination>
						<PaginationContent>
							<PaginationItem>
								<PaginationPrevious
									onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
								/>
							</PaginationItem>
							<PaginationItem>
								<PaginationNext
									onClick={() =>
										setPage((prev) =>
											(data?.data.Items?.length || 0) > prev * pageSize
												? prev + 1
												: prev,
										)
									}
								/>
							</PaginationItem>
						</PaginationContent>
					</Pagination>
				</div>
			)}
		</Form>
	);
}
