"use client";

import type React from "react";
import { CookiesProvider } from "react-cookie";
import { SWRConfig } from "swr";

interface IAppProvider {
	children: React.ReactNode;
}

export default function AppProvider({ children }: IAppProvider) {
	return (
		<>
			<CookiesProvider>
				<SWRConfig>{children}</SWRConfig>
			</CookiesProvider>
		</>
	);
}
