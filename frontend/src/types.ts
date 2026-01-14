// User types
export interface WonItem {
  id: number;
  title: string;
  image_url: string;
  final_price: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  profile_image_url?: string | null;
  won_items?: WonItem[];
}

// Profile types
export interface Profile {
  user: number;
  profile_image?: string;
  date_of_birth?: string;
}

export interface ProfileForm {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  profile_image?: File | null;
  profile_image_preview?: string;
}

// Item types
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
  bidder_name: string; // username
  amount: string; // decimal as string
  created_at: string; // ISO datetime
}

export interface Question {
  id: number;
  item: number; // item id
  author: number; // user id
  asker: number; // user id (same as author, for compatibility)
  asker_name: string; // username
  content: string;
  created_at: string; // ISO datetime
}

export interface Reply {
  id: number;
  question: number; // question id
  author: number; // user id
  author_name: string; // username
  content: string;
  created_at: string; // ISO datetime
}

// API Response types
export interface ApiError {
  error: string;
  details?: Record<string, string[]>;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
