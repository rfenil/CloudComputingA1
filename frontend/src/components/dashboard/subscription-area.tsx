"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useBackendMutation } from "@/hooks/useMutations";
import { useBackendQuery } from "@/hooks/useQuery";
import buildURLSearchParams from "@/lib/buildURLSearchParams";
import type { IResponse, IUnsubscribeRequest, MusicItem } from "@/types/main";
import { Music } from "lucide-react";
import Image from "next/image";
import { useState } from "react";
import { useCookies } from "react-cookie";
import { toast } from "sonner";

const URLs = {
	get: "/subscribed",
	post: "/unsubscribe",
};

export default function SubscriptionArea() {
	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	const [cookies, _setCookie, removeCookie] = useCookies<string>(["user_id"]);
	// Track which songs are currently being unsubscribed
	const [unsubscribingSongs, setUnsubscribingSongs] = useState<string[]>([]);

	const userId = cookies.user_id;
	const {
		data,
		mutate,
		isLoading: queryLoading,
	} = useBackendQuery<IResponse<MusicItem[]>>(
		`${URLs.get}${buildURLSearchParams({
			user_id: userId,
		})}`,
	);

	const { trigger: unSubscribeTrigger } = useBackendMutation<
		IUnsubscribeRequest,
		IResponse<null>
	>(URLs.post, {
		onSuccess: () => {
			toast.success("Successfully unsubscribed!");
			mutate();
		},
		onError: (error) => {
			toast.error(`Failed to unsubscribe: ${error.message || "Unknown error"}`);
		},
	});

	const unSubscribe = async (user_id: string, music_item: MusicItem) => {
		// Mark this specific song as loading
		setUnsubscribingSongs((prev) => [...prev, music_item.title]);

		try {
			await unSubscribeTrigger({
				user_id,
				artist: music_item.artist,
				title: music_item.title,
				year: music_item.year,
				album: music_item.album,
			});
		} finally {
			// Remove loading state for this song when done
			setUnsubscribingSongs((prev) =>
				prev.filter((id) => id !== music_item.title),
			);
		}
	};

	return (
		<Card className="h-[700px] overflow-auto">
			<CardHeader>
				<CardTitle>Your Subscriptions</CardTitle>
			</CardHeader>
			<CardContent>
				{queryLoading ? (
					<div className="flex items-center justify-center h-64">
						<p>Loading Subscriptions...</p>
					</div>
				) : data?.data?.length === 0 ? (
					<div className="flex flex-col items-center justify-center h-64 text-center">
						<Music className="h-12 w-12 text-muted-foreground mb-4" />
						<p className="text-muted-foreground">
							You haven&apos;t subscribed to any songs yet.
						</p>
						<p className="text-muted-foreground text-sm mt-2">
							Use the query area to find and subscribe to music.
						</p>
					</div>
				) : (
					<div className="space-y-4">
						{data?.data?.map((item) => {
							const isUnsubscribing = unsubscribingSongs.includes(item.id);

							return (
								<div
									key={item.id}
									className="border rounded-lg p-4 flex flex-col sm:flex-row gap-4"
								>
									<div className="relative w-24 h-24 flex-shrink-0 mx-auto sm:mx-0">
										{item.img_url ? (
											<Image
												src={item.img_url}
												alt={`${item.artist} image`}
												fill
												width={100}
												height={100}
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
											variant="destructive"
											size="sm"
											onClick={() => {
												unSubscribe(userId, item);
											}}
											disabled={isUnsubscribing}
										>
											{isUnsubscribing ? "Removing..." : "Remove"}
										</Button>
									</div>
								</div>
							);
						})}
					</div>
				)}
			</CardContent>
		</Card>
	);
}
