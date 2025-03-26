import { z } from "zod";

export const registerSchema = z.object({
	username: z
		.string()
		.min(2, "Username must be at least 2 characters long")
		.max(255, "Username name cannot exceed 255 characters"),
	email: z
		.string()
		.email(),
	password: z
		.string()
		.min(8, "Password must be at least 8 characters long")
		.max(128, "Password must not exceed 128 characters")
		.regex(/[A-Z]/, "Password must contain at least one uppercase letter")
		.regex(/[a-z]/, "Password must contain at least one lowercase letter")
		.regex(/\d/, "Password must contain at least one number")
		.regex(/[\W_]/, "Password must contain at least one special character"),
});
