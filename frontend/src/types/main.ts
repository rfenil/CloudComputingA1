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
