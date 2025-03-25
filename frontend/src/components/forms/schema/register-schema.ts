import { z } from "zod";

export const registerSchema = z.object({
	first_name: z
		.string()
		.min(2, "First name must be at least 2 characters long")
		.max(255, "First name cannot exceed 255 characters"),
	last_name: z
		.string()
		.min(2, "Last name must be at least 2 characters long")
		.max(255, "Last name cannot exceed 255 characters"),
	email: z
		.string()
		.email()
		.refine(
			(value) => {
				const pattern = /^s\d{7}[0-9]@student\.rmit\.edu\.au$/;
				return pattern.test(value);
			},
			{
				message: "Email must be in format s1234567[0-9]@student.rmit.edu.au",
			},
		),
	password: z
		.string()
		.min(8, "Password must be at least 8 characters long")
		.max(128, "Password must not exceed 128 characters")
		.regex(/[A-Z]/, "Password must contain at least one uppercase letter")
		.regex(/[a-z]/, "Password must contain at least one lowercase letter")
		.regex(/\d/, "Password must contain at least one number")
		.regex(/[\W_]/, "Password must contain at least one special character"),
});
