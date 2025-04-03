import { Button } from "@/components/ui/button";
import { useBackendMutation } from "@/hooks/useMutations";
import buildURLSearchParams from "@/lib/buildURLSearchParams";
import revalidate from "@/lib/revalidate";
import type { MusicItem } from "@/types/main";
import { Loader2 } from "lucide-react";
import Image from "next/image";
import React from "react";
import { Cookies } from "react-cookie";
import { toast } from "sonner";

interface ISubscriptionCardProps {
	item: MusicItem;
}

const URLs = {
	get: "/subscribed",
	post: "/unsubscribe",
};

export default function SubscriptionCard({ item }: ISubscriptionCardProps) {
	const { trigger, isMutating } = useBackendMutation(URLs.post, {
		onSuccess() {
			const user_id = new Cookies().get("user_id");
			revalidate(`${URLs.get}${buildURLSearchParams({ user_id })}`);
			toast.success("Subscription removed", { 
                description: `You have unsubscribed from ${item.title} by ${item.artist}.`,
            });
		},
        onError() {
            toast.error("Error removing subscription", { 
                description: "Failed to unsubscribe from this song. Please try again.",
            });
        }
	});

	const onRemoveClick = async () => {
		const user_id = new Cookies().get("user_id");
		await trigger({
			user_id: user_id,
			artist: item.artist,
			album: item.album,
			title: item.title,
			year: item.year,
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
					variant="destructive"
					size="sm"
					onClick={onRemoveClick}
					disabled={isMutating}
				>
					{isMutating && <Loader2 className="animate-spin" />}
					Remove
				</Button>
			</div>
		</div>
	);
}
