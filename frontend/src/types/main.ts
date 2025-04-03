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

export interface IMusicRequest {
	user_id: string;
}

export interface IUnsubscribeRequest {
	user_id: string;
	title: string;
	album: string;
	artist: string;
	year: string;
}

export interface ISubscribeRequest {
	user_id: string;
	title: string;
	album: string;
	artist: string;
	year: string;
}

export interface IResponse<T> {
	statusCode?: number;
	data?: T;
	message: string;
}
