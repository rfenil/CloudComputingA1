export interface IUserResponse {
	username: string;
	email: string;
	password: string;
}

export interface MusicItem {
	id: string;
	title: string;
	artist: string;
	album: string;
	year: string;
	img_url: string;
}

export interface IResponse<T> {
	statusCode?: number;
	data?: T;
	message: string;
}