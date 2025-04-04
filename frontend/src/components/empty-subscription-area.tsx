import { MusicIcon } from "lucide-react"

export default function EmptySubscriptionState() {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
      <div className="bg-muted/30 p-4 rounded-full">
        <MusicIcon className="h-12 w-12 text-muted-foreground" />
      </div>
      <h3 className="text-xl font-semibold">No subscriptions yet</h3>
      <p className="text-muted-foreground max-w-md">
        You haven&apos;t subscribed to any music yet. Search for your favorite songs, artists, or albums to get started.
      </p>
    </div>
  )
}

