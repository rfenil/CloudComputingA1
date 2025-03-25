import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";
import { ThemeProvider } from "next-themes";
import { SWRConfig } from "swr";

const primaryFont = Inter({
	subsets: ["latin"],
});

export const metadata: Metadata = {
	title: "Music Subscription",
	description: "Your go-to platform for music subscriptions",
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en" suppressHydrationWarning>
			<body className={`antialiased ${primaryFont.className}`}>
				<ThemeProvider
					attribute="class"
					defaultTheme="dark"
					enableSystem
					disableTransitionOnChange
				>
					<SWRConfig>{children}</SWRConfig>
				</ThemeProvider>
				<Toaster />
			</body>
		</html>
	);
}
