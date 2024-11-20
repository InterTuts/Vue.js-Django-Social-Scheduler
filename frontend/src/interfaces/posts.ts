export interface PostImage {
  path: string;
}

export interface Post {
  id: string;
  text: string;
  image: string;
  published: string;
  scheduled: string;
  created_at: number;
  networks: {
    network: {
      id: string;
      name: string;
      network_name: string;
    };
  }[];
}

export interface Posts {
  page: number;
  total: number;
  items: Post[];
  isLoading: boolean;
  noItems: string;
  modal: boolean;
  post?: Post;
  current_time: number;
}
