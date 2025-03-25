import QueryArea from "@/components/dashboard/query-area";
import SubscriptionArea from "@/components/dashboard/subscription-area";
import UserArea from "@/components/dashboard/user-area";

export default function Home() {
	return (
		<div className="container mx-auto p-4 space-y-8">
			<UserArea />
			<div className="grid grid-cols-1 md:grid-cols-2 gap-8">
				<SubscriptionArea />
				<QueryArea />
			</div>
		</div>
	);
}
