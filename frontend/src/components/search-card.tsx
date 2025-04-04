import { useBackendMutation } from "@/hooks/useMutations";
import buildURLSearchParams from "@/lib/buildURLSearchParams";
import revalidate from "@/lib/revalidate";
import type { MusicItem } from "@/types/main";
import { Loader2 } from "lucide-react";
import Image from "next/image";
import React from "react";
import { Cookies } from "react-cookie";
import { toast } from "sonner";
import { Button } from "./ui/button";

interface ISearchCardProps {
	item: MusicItem;
}

const URLs = {
	get: "/subscribed",
	post: "/subscribe",
};

export default function SearchCard({ item }: ISearchCardProps) {
	const { trigger, isMutating } = useBackendMutation(URLs.post, {
		onSuccess() {
			const user_id = new Cookies().get("user_id");
			revalidate(`${URLs.get}${buildURLSearchParams({ user_id: user_id })}`);
			toast.success("Subscription Successful", {
				description: `You are now subscribed to "${item.title}" by ${item.artist}.`,
			});
		},
		onError(error) {
			toast.error("Subscription Failed", {
				description:
					error.message || "An unexpected error occurred during subscription.",
			});
		},
	});
	const onSubscribe = async () => {
		const user_id = new Cookies().get("user_id");
		await trigger({
			user_id: user_id,
			artist: item.artist,
			title: item.title,
			album: item.album,
			year: item.year,
			img_url: item.img_url,
		});
	};
	return (
		<div className="border rounded-lg p-4 flex flex-col sm:flex-row gap-4">
			<div className="relative w-24 h-24 flex-shrink-0 mx-auto sm:mx-0">
				<Image
					src={item.img_url}
					alt={`${item.artist} image`}
					fill
					className="object-cover rounded-md"
				/>
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
					onClick={onSubscribe}
					disabled={isMutating}
				>
					{isMutating && <Loader2 className="animate-spin" />}
					Subscribe
				</Button>
			</div>
		</div>
	);
}
