/* eslint-disable @typescript-eslint/no-unused-vars */
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
import { useBackendQuery } from "@/hooks/useQuery";
import buildURLSearchParams from "@/lib/buildURLSearchParams";
import type { IResponse, ISearchResponse } from "@/types/main";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Search } from "lucide-react";
import React, { useState } from "react";
import { useForm } from "react-hook-form";
import type { z } from "zod";
import SearchDataList from "./search-data-list";
import { toast } from "sonner";
import EmptySearchState from "./empty-search-state";

const URLs = {
  get: "/search",
};

export default function SearchContainer() {
  const [queryParams, setQueryParams] = useState("");
  const url = queryParams
    ? `${URLs.get}${buildURLSearchParams(queryParams)}`
    : null;

  const { data, isLoading } = useBackendQuery<IResponse<ISearchResponse>>(url);

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
    try {
      const filteredValues = Object.fromEntries(
        Object.entries(values).filter(([_, value]) => value !== "")
      );

      if (Object.keys(filteredValues).length === 0) {
        toast.warning("Search fields empty", {
          description: "Please fill at least one field to search",
        });
      }

      const params = new URLSearchParams(
        filteredValues as Record<string, string>
      ).toString();
      setQueryParams(params);
    } catch (error) {
      console.log(`Error on submit ${error}`);
    }
  };

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
          {isLoading ? (
            <Loader2 className="animate-spin" />
          ) : (
            <Search className="ml-2 h-4 w-4" />
          )}
        </Button>
      </form>
      {data?.data?.Items?.length === 0 ? (
        <EmptySearchState />
      ) : (
        <SearchDataList items={data?.data?.Items} />
      )}
    </Form>
  );
}
