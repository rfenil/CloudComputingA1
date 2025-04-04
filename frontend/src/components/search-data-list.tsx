import type { MusicItem } from "@/types/main";
import React from "react";
import SearchCard from "./search-card";

interface ISearchDataListProps {
	items?: MusicItem[];
}

export default function SearchDataList({ items }: ISearchDataListProps) {
	return (
		<div className="mt-6 space-y-4">
			{items?.map((item) => (
				<SearchCard
					key={`${item.artist}#${item.album}#${item.title}`}
					item={item}
				/>
			))}
		</div>
	);
}
