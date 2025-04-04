import { SearchXIcon } from "lucide-react"

export default function EmptySearchState() {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
      <div className="bg-muted/30 p-4 rounded-full">
        <SearchXIcon className="h-12 w-12 text-muted-foreground" />
      </div>
      <h3 className="text-xl font-semibold">No results found</h3>
      <p className="text-muted-foreground max-w-md">
        We couldn&apos;t find any music matching your search criteria. Try adjusting your search terms or try a different
        combination.
      </p>
    </div>
  )
}

