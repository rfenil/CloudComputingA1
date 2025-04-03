"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useBackendMutation } from "@/hooks/useMutations";
import { useBackendQuery } from "@/hooks/useQuery";
import buildURLSearchParams from "@/lib/buildURLSearchParams";
import type { IResponse, ISubscribeRequest, MusicItem } from "@/types/main";
import Image from "next/image";
import { useEffect, useState } from "react";
import { useCookies } from "react-cookie";
import { toast } from "sonner";

const musicItems: MusicItem[] = [
	{
		id: "359a615a-07de-4cf6-9afa-e65b420cf03e",
		title: "Come Monday",
		artist: "Jimmy Buffett",
		album: "Living and Dying in 3/4 Time",
		year: "1974",
		img_url:
			"https://a1-projectgroup-31-krish.s3.us-east-1.amazonaws.com/artist_images/John_Lennon_Watching_the_Wheels.jpg",
	},
	{
		id: "5c616ec5-c82f-4b26-9725-1a53dba8ac3a",
		title: "The Sound of Silence",
		artist: "Simon & Garfunkel",
		album: "Wednesday Morning, 3 A.M.",
		year: "1964",
		img_url:
			"https://a1-projectgroup-31-krish.s3.us-east-1.amazonaws.com/artist_images/John_Lennon_Watching_the_Wheels.jpg",
	},
	{
		id: "eca3e7da-0b23-4be6-8c54-a78a6a53f626",
		title: "Imagine",
		artist: "John Lennon",
		album: "Imagine",
		year: "1971",
		img_url:
			"https://a1-projectgroup-31-krish.s3.us-east-1.amazonaws.com/artist_images/John_Lennon_Watching_the_Wheels.jpg",
	},
];

const URLs = {
	post: "/subscribe",
	get: "/subscribed",
};

export default function BrowseArea() {
	const { trigger: subscribeTrigger } = useBackendMutation<
		ISubscribeRequest,
		IResponse<null>
	>(URLs.post, {
		onSuccess: () => {
			toast.success("Successfully subscribed!");
		},
		onError: (error) => {
			toast.error(`Failed to subscribe: ${error.message || "Unknown error"}`);
		},
	});

	const [subscribedSongs, setSubscribedSongs] = useState<string[]>([]);
	const [loadingSongs, setLoadingSongs] = useState<string[]>([]);
	const [cookies] = useCookies(["user_id"]);
	const userId = cookies.user_id;

	const { data: subscriptionData, mutate } = useBackendQuery<
		IResponse<MusicItem[]>
	>(`${URLs.get}${buildURLSearchParams({ user_id: userId })}`, {
		onSuccess: (res) => {
			if (res?.data) {
				setSubscribedSongs(res.data.map((item) => item.id));
			}
		},
	});

	useEffect(() => {
		if (subscriptionData?.data) {
			setSubscribedSongs(subscriptionData.data.map((item) => item.id));
		}
	}, [subscriptionData]);

	const handleSubscribe = async (songId: string) => {
		if (!userId) {
			toast.error("Please log in to subscribe.");
			return;
		}

		setLoadingSongs((prev) => [...prev, songId]);

		try {
			await subscribeTrigger({ user_id: userId, song_id: songId });
			setSubscribedSongs((prev) => [...prev, songId]);
			mutate();
		} finally {
			setLoadingSongs((prev) => prev.filter((id) => id !== songId));
		}
	};

	return (
		<Card className="h-fit overflow-auto">
			<CardHeader>
				<CardTitle>Browse Music</CardTitle>
			</CardHeader>
			<CardContent className="flex flex-wrap gap-4">
				{musicItems.map((item) => {
					const isSubscribed = subscribedSongs.includes(item.id);
					const isLoading = loadingSongs.includes(item.id);

					return (
						<div
							key={item.id}
							className="flex flex-col border-2 p-4 rounded-lg gap-4 w-[300px]"
						>
							<div className="relative w-full aspect-square">
								<Image
									src={item.img_url || "/placeholder.svg"}
									alt={`${item.artist} image`}
									fill
									className="object-cover rounded-md"
								/>
							</div>

							<div className="space-y-2">
								<h3 className="font-medium">{item.title}</h3>
								<div className="text-sm text-muted-foreground">
									<p>Artist: {item.artist}</p>
									<p>Album: {item.album}</p>
									<p>Year: {item.year}</p>
								</div>
								<Button
									size="sm"
									className="w-full"
									onClick={() => handleSubscribe(item.id)}
									disabled={isSubscribed || isLoading}
								>
									{isSubscribed
										? "Subscribed"
										: isLoading
											? "Subscribing..."
											: "Subscribe"}
								</Button>
							</div>
						</div>
					);
				})}
			</CardContent>
		</Card>
	);
}
