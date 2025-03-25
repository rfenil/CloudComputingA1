import { z } from "zod";

export const loginSchema = z.object({
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
	password: z.string().nonempty("Password cannot be empty"),
});
