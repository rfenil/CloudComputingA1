import type React from "react";

interface ICenterContainerProps {
	children: React.ReactNode;
}

export default function CenterContainer({ children }: ICenterContainerProps) {
	return (
		<div className="w-screen h-screen flex items-center justify-center">
			{children}
		</div>
	);
}
