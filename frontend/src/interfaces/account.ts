export interface Account {
  accountId: string;
  networkName: string;
  checked: boolean;
}

export interface AccountsList {
  accountId: string;
  accountName: string;
  networkName: string;
  checked: boolean;
}

export interface NetworksList {
  id: string;
  name: string;
  network_name: string;
}

export interface Menu {
  openMenu: boolean;
  activeTab: string;
  networks: {
    [key: string]: Array<{
      id: string;
      name: string;
      checked: boolean;
    }>;
  };
}
