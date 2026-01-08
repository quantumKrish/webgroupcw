export interface Item {
  id: number;
  owner: number; // user id
  title: string;
  description: string;
  starting_price: string; // decimal as string
  image_url: string | null;
  ends_at: string; // ISO datetime
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
  // convenience field some endpoints may add
  current_price?: string;
}

export interface Bid {
  id: number;
  item: number; // item id
  bidder: number; // user id
  amount: string; // decimal as string
  created_at: string; // ISO datetime
}

export interface Question {
  id: number;
  item: number; // item id
  author: number; // user id
  content: string;
  created_at: string; // ISO datetime
}

export interface Reply {
  id: number;
  question: number; // question id
  author: number; // user id
  content: string;
  created_at: string; // ISO datetime
}
