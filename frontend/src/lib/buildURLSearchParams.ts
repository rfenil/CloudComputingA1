import { isString, pickBy } from "lodash";

export default function buildURLSearchParams(
  params?: Record<string, string | null | undefined> | string
) {
  const urlSearchParams = new URLSearchParams(
    typeof params === "string" ? params : pickBy(params, isString)
  );
  urlSearchParams.sort();
  return urlSearchParams.toString() ? `?${urlSearchParams}` : "";
}
