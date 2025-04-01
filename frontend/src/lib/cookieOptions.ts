// eslint-disable-next-line import/prefer-default-export
export const cookieOptions = {
	path: "/",
	sameSite: "lax" as const,
	secure: true,
	domain: global.window?.location.hostname,
};
