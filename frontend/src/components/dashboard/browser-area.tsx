import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { MusicItem } from "@/types/main";
import Image from "next/image";

const musicItems: MusicItem[] = [
	{
		id: "1",
		title: "Come Monday",
		artist: "Jimmy Buffett",
		album: "Living and Dying in 3/4 Time",
		year: "1974",
		imageUrl:
			"https://raw.githubusercontent.com/YingZhang2015/cc/main/TheTallestManOnEarth.jpg",
	},
];

export default function BrowseArea() {
	return (
		<Card className="h-fit overflow-auto">
			<CardHeader>
				<CardTitle>Browse Music</CardTitle>
			</CardHeader>
			<CardContent className="flex">
				{musicItems.map((item) => {
					return (
						<div
							key={item.id}
							className="flex flex-col border-2 p-4 rounded-lg gap-4"
						>
							<div className="relative w-24 h-24">
								<Image
									src={item.imageUrl || "/placeholder.svg"}
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
								<Button size="sm" className="w-full">
									Subscribe
								</Button>
							</div>
						</div>
					);
				})}
			</CardContent>
		</Card>
	);
}
