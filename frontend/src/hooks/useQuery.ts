import useSWR, { SWRConfiguration } from "swr";
import { getFetcher } from "@/lib/fetcher";
import { AuthServerUrl } from "@/lib/constant";

type TKey = string | [string, Record<string, string>] | null;

function formatKey(key: TKey) {
  if (key) {
    if (Array.isArray(key)) {
      return [...key];
    }
    return [key];
  }
  return null;
}

function useQuery<Data>(
  key: TKey,
  fetcher: (
    _key: string,
    _options?: { arg: Record<string, string> }
  ) => Promise<Data>,
  config?: SWRConfiguration<Data, Error>
) {
  return useSWR<Data, Error>(formatKey(key), fetcher, {
    errorRetryCount: 3,
    ...config,
  });
}

export function useAuthServerQuery<Data>(
  key: string | null,
  config?: SWRConfiguration<Data, Error>
) {
  return useQuery<Data>(key, getFetcher(AuthServerUrl), config);
}