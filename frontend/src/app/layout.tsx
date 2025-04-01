import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import AppProvider from "@/context/AppProvider";
import { ThemeProvider } from "next-themes";
import { Toaster } from "sonner";

const primaryFont = Inter({
	subsets: ["latin"],
	display: "swap",
	adjustFontFallback: false,
});

export const metadata: Metadata = {
	title: {
		default: "Music Subscription",
		template: "%s | Music Subscription",
	},
	description: "Your go-to platform for music subscriptions",
	keywords: ["music", "subscription", "streaming"],
	authors: [{ name: "Your Name", url: "https://44.212.204.204" }],
	openGraph: {
		type: "website",
		locale: "en_US",
		url: "https://44.212.204.204",
		siteName: "Music Subscription",
	},
	metadataBase: new URL("https://44.212.204.204"),
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
					<AppProvider>{children}</AppProvider>
				</ThemeProvider>
				<Toaster />
			</body>
		</html>
	);
}
