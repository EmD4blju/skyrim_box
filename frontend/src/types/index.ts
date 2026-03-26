export interface Item {
  id: number;
  name: string;
  description: string;
  image_url?: string;
}

export interface Comment {
  id: number;
  content: string;
  user_id: number;
  item_id: number;
}
