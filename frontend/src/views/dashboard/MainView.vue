<script setup lang="ts">
// Installed Utils
import { vInfiniteScroll } from '@vueuse/components';
import { useI18n } from 'vue-i18n';
import { useHead } from '@vueuse/head';
import type { Ref } from 'vue';
import { ref, reactive, watch, onMounted } from 'vue';
import { VTimePicker } from 'vuetify/labs/VTimePicker';
import { useNotification } from '@kyvg/vue3-notification';

// App Utils
import axios, { type AxiosResponse } from '@/axios';
import type {
  Account,
  AccountsList,
  NetworksList,
  Menu,
} from '@/interfaces/account';
import type ApiResponse from '@/interfaces/apiResponse';
import type { Post, Posts, PostImage } from '@/interfaces/posts';

// Get i18n functions
const { t } = useI18n();

// Get the notify method
const { notify } = useNotification();

// Set page title and description
useHead({
  title: t('dashboard'),
  meta: [
    { name: 'description', content: () => t('dashboard_page_description') },
    {
      name: 'keywords',
      content: () => 'dashboard, account, registration, page',
    },
  ],
});

// Accounts menu
const accountsMenu = reactive<Menu>({
  openMenu: false,
  activeTab: 'facebook-network-tab',
  networks: {
    facebook_pages: [],
    threads: [],
  },
});

// Detect when the accounts menu is open
watch(
  () => accountsMenu.openMenu,
  (newMenu, oldMenu) => {
    if (!oldMenu && newMenu) {
      fetchNetworks();
    }
  },
);

// Posts parameters
const posts = reactive<Posts>({
  page: 1,
  total: 0,
  items: [],
  isLoading: false,
  noItems: '',
  modal: false,
  current_time: 0,
});

// Function to handle scroll and fetch more data when reaching bottom
const handleScroll = () => {
  if ((posts.page - 1) * 10 < posts.total) {
    fetchPosts();
  }
};

// Function to fetch posts
const fetchPosts = async () => {
  posts.isLoading = true;
  try {
    // Send request
    const response: AxiosResponse<
      ApiResponse<{
        items: Post[];
        total: number;
        current_time: number;
      }>
    > = await axios.get(`api/posts/list?page=${posts.page}`);
    // Check if the message is success
    if (response.data.content) {
      posts.page += 1;
      posts.total = response.data.content.total;
      posts.items = [...[...posts.items], ...response.data.content.items];
      posts.current_time = response.data.content.current_time;
    } else if (response.data.message) {
      posts.noItems = response.data.message;
    }
  } catch (error) {
    console.error(error);
  } finally {
    posts.isLoading = false;
  }
};

/**
 * Get post's data
 *
 * @param string postId
 */
const getPost = async (postId: string) => {
  try {
    // Send request
    const response: AxiosResponse<ApiResponse<Post>> = await axios.get(
      `api/posts/${postId}`,
    );

    if (response.data.success && response.data.content) {
      posts.modal = true;
      posts.post = response.data.content;
    } else {
      notify({
        type: 'error',
        text: response.data.message,
      });
    }
  } catch (error) {
    console.error(error);
  }
};

// Function to fetch last social accounts
const fetchLastNetworks = async () => {
  try {
    // Send request
    const response: AxiosResponse<ApiResponse<NetworksList[]>> =
      await axios.get(`api/networks/last`);
    if (response.data.success && response.data.content) {
      const totalAccounts = response.data.content.length;
      for (let a = 0; a < totalAccounts; a++) {
        selectedAccounts.value[response.data.content[a].id] = {
          accountId: response.data.content[a].id,
          accountName: response.data.content[a].name,
          networkName: response.data.content[a].network_name,
          checked: false,
        };
      }
    }
  } catch (error) {
    console.error(error);
  }
};

// Function to fetch all social accounts
const fetchNetworks = async () => {
  accountsMenu.networks.facebook_pages = [];
  accountsMenu.networks.threads = [];
  try {
    // Send request
    const response: AxiosResponse<
      ApiResponse<
        {
          id: string;
          name: string;
          network_name: string;
        }[]
      >
    > = await axios.get(`api/networks/list`);
    if (response.data.success && response.data.content) {
      const totalAccounts = response.data.content.length;
      for (let a = 0; a < totalAccounts; a++) {
        if (response.data.content[a].network_name === 'facebook_pages') {
          accountsMenu.networks.facebook_pages.push({
            id: response.data.content[a].id,
            name: response.data.content[a].name,
            checked: false,
          });
        } else if (response.data.content[a].network_name === 'threads') {
          accountsMenu.networks.threads.push({
            id: response.data.content[a].id,
            name: response.data.content[a].name,
            checked: false,
          });
        }
      }
    }
  } catch (error) {
    console.error(error);
  }
};

// Selected accounts list
const selectedAccounts = ref<Record<string, AccountsList>>({});

/**
 * Select or Unselect Account
 *
 * @param object account
 */
const selectAccount = async (account: {
  accountId: string;
  accountName: string;
  networkName: string;
  checked: boolean;
}) => {
  if (typeof selectedAccounts.value[account.accountId] !== 'undefined') {
    if (selectedAccounts.value[account.accountId].checked) {
      selectedAccounts.value[account.accountId].checked = false;
      delete selectedAccounts.value[account.accountId];
    } else {
      selectedAccounts.value[account.accountId].checked = true;
    }
  } else {
    selectedAccounts.value[account.accountId] = account;
  }
};

/**
 * Delete Account
 *
 * @param string accountId
 */
const deleteAccount = async (accountId: string) => {
  try {
    // Send request
    const response: AxiosResponse<ApiResponse<null>> = await axios.delete(
      `api/networks/${accountId}`,
    );
    if (response.data.success) {
      notify({
        type: 'success',
        text: response.data.message,
      });
      if (typeof selectedAccounts.value[accountId] !== 'undefined') {
        delete selectedAccounts.value[accountId];
      }
      // Reload networks
      await Promise.all([fetchNetworks(), fetchLastNetworks()]);
    } else {
      notify({
        type: 'error',
        text: response.data.message,
      });
    }
  } catch (error) {
    console.error(error);
  }
};

/**
 * Verify if an account is selected or unselected
 *
 * @param string accountId
 */
const isSelectedAccount = (accountId: string) => {
  return (
    typeof selectedAccounts.value[accountId] !== 'undefined' &&
    selectedAccounts.value[accountId].checked
  );
};

/**
 * Get abbreviations for name
 *
 * @param string name
 *
 * @return string
 */
const nameAbbreviation = (name: string) => {
  const second = name.split(' ').length > 1 ? name.split(' ')[1].charAt(0) : '';
  return name.charAt(0) + second;
};

/**
 * Get account cover
 *
 * @param string networkName
 *
 * @return string
 */
const accountCover = (networkName: string) => {
  if (networkName === 'facebook_pages') {
    return 'cover-fb';
  } else if (networkName === 'threads') {
    return 'cover-threads';
  } else {
    return '';
  }
};

const selectUnselectAccount = (accountId: string, event: Event) => {
  const target = event.target as HTMLInputElement;
  if (!target.checked) {
    delete selectedAccounts.value[accountId];
  } else {
    selectedAccounts.value[accountId].checked = true;
  }
};

/**
 * Check if date is today
 *
 * @param number date
 */
const isToday = (date: number) => {
  const today: Date = new Date();
  const inputDate: Date = new Date(date);
  today.setHours(0, 0, 0, 0);
  inputDate.setHours(0, 0, 0, 0);
  return today.getTime() === inputDate.getTime();
};

/**
 * Get image url
 *
 * @param string path
 */
const imageUrl = (path: string) => {
  return import.meta.env.VITE_APP_API_URL + path;
};

// Scheduler reactive data
const scheduler = reactive({
  schedulePost: false,
  minDate: new Date().toISOString().substr(0, 10),
  minHour: new Date().getHours() + ':' + new Date().getMinutes(),
  selectedDate: null,
  selectedTime: null,
});

// Detect updates in the scheduler object
watch(scheduler, (newValue) => {
  if (newValue.selectedDate && isToday(newValue.selectedDate)) {
    scheduler.minHour = new Date().getHours() + ':' + new Date().getMinutes();
  } else {
    scheduler.minHour = '00:00';
  }
});

// Post reactive data
const post = reactive({
  text: '',
  image: '',
  publish: false,
  schedule: false,
});

/**
 * Detect image select
 *
 * @param Event event
 */
const onImageSelected = async (event: Event) => {
  // Create a new FormData object
  const formData = new FormData();

  // Prepare the input
  const input = event.target as HTMLInputElement;

  // Verify if a file was selected
  if (input.files && input.files[0]) {
    // Add file to form data
    formData.append('image', input.files[0]);

    try {
      // Send request
      const response: AxiosResponse<ApiResponse<PostImage>> = await axios.post(
        'api/media/upload-image',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        },
      );

      // Check if the message is success
      if (response.data.success) {
        post.image = response.data.content?.path ?? '';
        notify({
          type: 'success',
          text: response.data.message,
        });
      } else {
        notify({
          type: 'error',
          text: response.data.message,
        });
      }
    } catch (error) {
      console.error(error);
    }
  }
};

// Post form
const form: Ref<{ reset: () => void } | null> = ref(null);

/**
 * Publish post
 */
const publishPost = async () => {
  // Enable the animation
  post.publish = true;
  try {
    // Accounts container
    const accounts = [];

    // Get all selected accounts
    const taccounts = Object.values(selectedAccounts.value);

    // Chech if accounts exists
    if (taccounts.length > 0) {
      // List all accounts
      for (const account of taccounts) {
        if (account.checked) {
          accounts.push({
            id: account.accountId,
            network_name: account.networkName,
          });
        }
      }
    }

    // Chech if accounts were selected
    if (accounts.length < 1) {
      // Disable the animation
      post.publish = false;
      notify({
        type: 'error',
        text: t('please_select_an_account'),
      });
      return;
    }

    // Send request
    const response: AxiosResponse<ApiResponse<null>> = await axios.post(
      'api/posts/create',
      {
        text: post.text,
        image: post.image,
        networks: accounts,
      },
    );

    // Check if the message is success
    if (response.data.success) {
      posts.page = 1;
      posts.total = 0;
      posts.items = [];
      post.text = '';
      post.image = '';
      if (form.value && typeof form.value.reset === 'function') {
        form.value.reset();
      }
      // Chech if accounts exists
      if (taccounts.length > 0) {
        // List all accounts
        for (const account of taccounts) {
          selectedAccounts.value[account.accountId].checked = false;
        }
      }
      fetchPosts();
      notify({
        type: 'success',
        text: response.data.message,
      });
    } else {
      notify({
        type: 'error',
        text: response.data.message,
      });
    }
  } catch (error) {
    console.error(error);
  }

  // Disable the animation
  post.publish = false;
};

/**
 * Schedule post
 */
const schedulePost = async () => {
  // Enable the animation
  post.schedule = true;

  try {
    // Accounts container
    const accounts = [];

    // Get all selected accounts
    const taccounts: Account[] = Object.values(selectedAccounts.value);

    // Chech if accounts exists
    if (taccounts.length > 0) {
      // List all accounts
      for (const account of taccounts) {
        if (account.checked) {
          accounts.push({
            id: account.accountId,
            network_name: account.networkName,
          });
        }
      }
    }

    // Chech if accounts were selected
    if (accounts.length < 1) {
      // Disable the animation
      post.publish = false;
      notify({
        type: 'error',
        text: t('please_select_an_account'),
      });
      return;
    }

    // Get the selected date
    const selectedDate = new Date(scheduler.selectedDate ?? '');

    // Get the selected time
    const selectedTime = !scheduler.selectedTime
      ? new Date().getHours() + ':' + new Date().getMinutes()
      : scheduler.selectedTime;

    // Schedule time for post
    const scheduledTime = {
      year: selectedDate.getFullYear(),
      month: String(selectedDate.getMonth() + 1).padStart(2, '0'),
      date: String(selectedDate.getDate()).padStart(2, '0'),
      hours: selectedTime.split(':')[0],
      minutes: selectedTime.split(':')[1],
    };

    // Send request
    const response: AxiosResponse<ApiResponse<null>> = await axios.post(
      'api/posts/schedule',
      {
        text: post.text,
        image: post.image,
        networks: accounts,
        scheduled: scheduledTime,
      },
    );

    // Check if the message is success
    if (response.data.success) {
      posts.page = 1;
      posts.total = 0;
      posts.items = [];
      post.text = '';
      post.image = '';
      if (form.value && typeof form.value.reset === 'function') {
        form.value.reset();
      }
      scheduler.selectedDate = null;
      scheduler.selectedTime = null;
      scheduler.schedulePost = false;
      // Chech if accounts exists
      if (taccounts.length > 0) {
        // List all accounts
        for (const account of taccounts) {
          selectedAccounts.value[account.accountId].checked = false;
        }
      }
      fetchPosts();
      notify({
        type: 'success',
        text: response.data.message,
      });
    } else {
      notify({
        type: 'error',
        text: response.data.message,
      });
    }
  } catch (error) {
    console.error(error);
  }

  // Disable the animation
  post.schedule = false;
};

/**
 * Cancel a scheduled post
 *
 * @param string post's id
 */
const cancelScheduledPost = async (postId: string) => {
  try {
    // Send request
    const response: AxiosResponse<ApiResponse<null>> = await axios.post(
      `api/posts/cancel/${postId}`,
    );
    if (response.data.success) {
      notify({
        type: 'success',
        text: response.data.message,
      });
      posts.page = 1;
      posts.total = 0;
      posts.items = [];
      // Reload posts
      await Promise.all([getPost(postId), fetchPosts()]);
    } else {
      notify({
        type: 'error',
        text: response.data.message,
      });
    }
  } catch (error) {
    console.error(error);
  }
};

// Empty the image field
const clearImage = () => {
  post.image = '';
};

/**
 * Connect social account
 *
 * @param string network
 */
const socialConnect = (network: string) => {
  // Set popup's url
  const popup_url = import.meta.env.VITE_APP_WEBSITE_URL + 'connect/' + network;

  // Get popup's position from left
  const from_left =
    window.screenLeft != undefined ? window.screenLeft : window.screenX;

  // Get popup's width
  const width = window.innerWidth
    ? window.innerWidth
    : document.documentElement.clientWidth
      ? document.documentElement.clientWidth
      : screen.width;

  // Get popup's height
  const height = window.innerHeight
    ? window.innerHeight
    : document.documentElement.clientHeight
      ? document.documentElement.clientHeight
      : screen.height;

  // Calculate new left poition
  const left = width / 2 - width / 2 / 2 + from_left;

  // Set default top position
  const top = 50;

  // Open popup
  const networkWindow = window.open(
    popup_url,
    'Connect Account',
    'scrollbars=yes, width=' +
      width / 2 +
      ', height=' +
      height / 1.3 +
      ', top=' +
      top +
      ', left=' +
      left,
  );

  // Set focus
  if (typeof window.focus === 'function' && networkWindow) {
    networkWindow.focus();
  }
};

// Wait until the component is mounted
onMounted(async () => {
  // Load posts and networks
  await Promise.all([fetchPosts(), fetchLastNetworks()]);

  // Reload accounts
  window.reloadAccounts = () => {
    // Logic to reload accounts
    fetchNetworks();
  };
});

const calculate_time = (from: number, to: number) => {
  // Set calculation time
  let calculate: number = to - from;

  // Set after variable
  let after: string = '<span class="mdi mdi-history time-icon"></span>';

  // Set before variable
  let before: string = ' ' + t('ago');

  // Define calc variable
  let calc: number;

  // Verify if time is older than now
  if (calculate < 0) {
    // Set absolute value of a calculated time
    calculate = Math.abs(calculate);

    // Set icon
    after = '<span class="mdi mdi-invoice-clock-outline time-icon"></span>';

    // Empty before
    before = '';
  }

  // Calculate time
  if (calculate < 60) {
    return after + t('just_now');
  } else if (calculate < 3600) {
    calc = calculate / 60;
    calc = Math.round(calc);
    return after + calc + ' ' + t('minutes') + before;
  } else if (calculate < 86400) {
    calc = calculate / 3600;
    calc = Math.round(calc);
    return after + calc + ' ' + t('hours') + before;
  } else if (calculate >= 86400) {
    calc = calculate / 86400;
    calc = Math.round(calc);
    return after + calc + ' ' + t('days') + before;
  }
};
</script>
<template>
  <v-app>
    <v-app-bar class="composer-toolbar">
      <v-img
        src="/logo.png"
        max-width="145"
        height="30"
        alt="Scheduler Logo"
      ></v-img>
      <v-spacer></v-spacer>
      <v-btn variant="text" to="/logout">
        {{ $t('logout') }}
        <span class="mdi mdi-logout"></span>
      </v-btn>
    </v-app-bar>
    <v-main class="composer-main">
      <v-container fluid class="pa-0 composer-container">
        <v-row no-gutters>
          <v-col
            cols="12"
            md="4"
            lg="3"
            class="posts-list"
            v-infinite-scroll="[handleScroll, { distance: 10 }]"
          >
            <v-row dense class="pa-3">
              <v-col cols="12" v-if="posts.items.length">
                <v-card
                  class="mx-auto post-card"
                  v-for="item in posts.items"
                  :key="item.id"
                >
                  <v-card-title class="post-card-title">
                    <span class="post-status-published" v-if="item.published">
                      {{ $t('published') }}
                    </span>
                    <span
                      class="post-status-scheduled"
                      v-else-if="item.scheduled"
                    >
                      {{ $t('scheduled') }}
                    </span>
                    <span
                      class="post-status-failed"
                      v-else-if="!item.published"
                    >
                      {{ $t('failed') }}
                    </span>
                    <small
                      v-html="
                        calculate_time(
                          item.created_at / 1000,
                          posts.current_time,
                        )
                      "
                    ></small>
                  </v-card-title>

                  <v-card-text class="post-text post-card-text">
                    {{ item.text }}
                  </v-card-text>

                  <v-card-actions class="justify-end post-card-actions">
                    <v-btn
                      color="secondary post-card-button"
                      @click="getPost(item.id)"
                    >
                      <span class="mdi mdi-note-search-outline"></span>
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-col>
              <v-col cols="12" v-else>
                <p class="no-posts">{{ posts.noItems }}</p>
              </v-col>
            </v-row>
            <div class="v-spinner" v-if="posts.isLoading">
              <div class="v-pulse v-pulse1"></div>
              <div class="v-pulse v-pulse2"></div>
              <div class="v-pulse v-pulse3"></div>
            </div>
          </v-col>
          <v-col cols="12" md="8" lg="9" class="posts-composer">
            <v-row>
              <v-col
                cols="12"
                lg="8"
                offset-lg="2"
                xl="10"
                offset-xl="1"
                xxl="6"
                offset-xxl="3"
              >
                <v-row>
                  <v-col cols="12" md="6">
                    <v-form ref="form">
                      <v-row>
                        <v-col
                          class="d-flex"
                          cols="12"
                          md="9"
                          v-if="Object.keys(selectedAccounts).length"
                        >
                          <div
                            class="post-profile"
                            v-for="account in Object.values(selectedAccounts)"
                            :key="account.accountId"
                          >
                            <input
                              type="checkbox"
                              :id="'post-account-' + account.accountId"
                              :checked="account.checked"
                              @change="
                                selectUnselectAccount(account.accountId, $event)
                              "
                            />
                            <label :for="'post-account-' + account.accountId">
                              <span
                                class="mdi mdi-checkbox-marked-circle-outline"
                              ></span>
                              <span
                                class="cover"
                                :class="accountCover(account.networkName)"
                                >{{
                                  nameAbbreviation(account.accountName)
                                }}</span
                              >
                              <small>{{ account.accountName }}</small>
                            </label>
                          </div>
                        </v-col>
                        <v-col class="d-flex" cols="12" md="9" v-else></v-col>
                        <v-col class="d-flex justify-end" cols="12" md="3">
                          <v-menu
                            v-model="accountsMenu.openMenu"
                            :close-on-content-click="false"
                            location="end"
                          >
                            <template v-slot:activator="{ props }">
                              <v-btn class="accounts-menu-btn" v-bind="props">
                                <span class="mdi mdi-plus"></span>
                              </v-btn>
                            </template>
                            <v-card
                              class="accounts-menu-popover"
                              min-width="350"
                              min-height="350"
                            >
                              <div class="d-flex flex-row social-list">
                                <v-tabs
                                  v-model="accountsMenu.activeTab"
                                  class="social-list-tabs"
                                  color="primary"
                                  direction="vertical"
                                >
                                  <v-tab value="facebook-network-tab">
                                    <v-img
                                      src="/fb-blue.png"
                                      width="22"
                                      height="22"
                                      alt="Facebook Icon"
                                    ></v-img>
                                  </v-tab>
                                  <v-tab value="threads-network-tab">
                                    <v-img
                                      src="/threads.png"
                                      width="22"
                                      height="22"
                                      alt="Threads Icon"
                                    ></v-img>
                                  </v-tab>
                                </v-tabs>
                                <v-tabs-window v-model="accountsMenu.activeTab">
                                  <v-tabs-window-item
                                    value="facebook-network-tab"
                                  >
                                    <v-card flat>
                                      <v-card-text>
                                        <v-row>
                                          <v-col cols="12">
                                            <v-btn
                                              class="facebook-network-btn"
                                              @click="socialConnect('facebook')"
                                            >
                                              {{ t('continue_with_facebook') }}
                                            </v-btn>
                                          </v-col>
                                        </v-row>
                                        <v-row>
                                          <v-col
                                            cols="12"
                                            class="network-accounts-list"
                                            v-if="
                                              accountsMenu.networks
                                                .facebook_pages.length > 0
                                            "
                                          >
                                            <v-btn-toggle
                                              class="network-account-group mr-3"
                                              v-for="account in accountsMenu
                                                .networks.facebook_pages"
                                              :key="account.id"
                                            >
                                              <v-btn
                                                max-width="100px"
                                                @click="
                                                  selectAccount({
                                                    accountId: account.id,
                                                    accountName: account.name,
                                                    networkName:
                                                      'facebook_pages',
                                                    checked: true,
                                                  })
                                                "
                                              >
                                                {{ account.name }}
                                              </v-btn>

                                              <v-btn
                                                :class="{
                                                  'selected-account':
                                                    isSelectedAccount(
                                                      account.id,
                                                    ),
                                                }"
                                                value="center"
                                                @click="
                                                  deleteAccount(account.id)
                                                "
                                              >
                                                <span
                                                  class="mdi mdi-trash-can-outline"
                                                ></span>
                                              </v-btn>
                                            </v-btn-toggle>
                                          </v-col>
                                          <v-col
                                            cols="12"
                                            class="network-accounts-no-list"
                                            v-else
                                          >
                                            <p>
                                              {{ t('no_pages_were_found') }}
                                            </p>
                                          </v-col>
                                        </v-row>
                                      </v-card-text>
                                    </v-card>
                                  </v-tabs-window-item>
                                  <v-tabs-window-item
                                    value="threads-network-tab"
                                  >
                                    <v-card flat>
                                      <v-card-text>
                                        <v-row>
                                          <v-col cols="12">
                                            <v-btn
                                              class="threads-network-btn"
                                              @click="socialConnect('threads')"
                                            >
                                              {{ t('continue_with_threads') }}
                                            </v-btn>
                                          </v-col>
                                        </v-row>
                                        <v-row>
                                          <v-col
                                            cols="12"
                                            class="network-accounts-list"
                                            v-if="
                                              accountsMenu.networks.threads
                                                .length > 0
                                            "
                                          >
                                            <v-btn-toggle
                                              class="network-account-group mr-3"
                                              v-for="account in accountsMenu
                                                .networks.threads"
                                              :key="account.id"
                                            >
                                              <v-btn
                                                max-width="100px"
                                                @click="
                                                  selectAccount({
                                                    accountId: account.id,
                                                    accountName: account.name,
                                                    networkName: 'threads',
                                                    checked: true,
                                                  })
                                                "
                                              >
                                                {{ account.name }}
                                              </v-btn>

                                              <v-btn
                                                :class="{
                                                  'selected-account':
                                                    isSelectedAccount(
                                                      account.id,
                                                    ),
                                                }"
                                                value="center"
                                                @click="
                                                  deleteAccount(account.id)
                                                "
                                              >
                                                <span
                                                  class="mdi mdi-trash-can-outline"
                                                ></span>
                                              </v-btn>
                                            </v-btn-toggle>
                                          </v-col>
                                          <v-col
                                            cols="12"
                                            class="network-accounts-no-list"
                                            v-else
                                          >
                                            <p>
                                              {{ t('no_accounts_were_found') }}
                                            </p>
                                          </v-col>
                                        </v-row>
                                      </v-card-text>
                                    </v-card>
                                  </v-tabs-window-item>
                                </v-tabs-window>
                              </div>
                            </v-card>
                          </v-menu>
                        </v-col>
                      </v-row>
                      <v-row>
                        <v-col cols="12">
                          <v-card class="composer">
                            <v-card-text>
                              <v-textarea
                                :label="t('write_something')"
                                counter="1200"
                                class="composer-textarea"
                                v-model="post.text"
                              ></v-textarea>
                            </v-card-text>
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row>
                        <v-col cols="12">
                          <v-file-input
                            accept="image/png, image/jpeg, image/bmp"
                            :label="t('post_image')"
                            class="composer-image"
                            hide-details
                            prepend-icon="mdi-camera"
                            @change="onImageSelected"
                            @click:clear="clearImage"
                          ></v-file-input>
                        </v-col>
                      </v-row>
                      <v-row>
                        <v-col cols="12" class="d-flex justify-end">
                          <v-btn append-icon="mdi-cached" v-if="post.publish">
                            {{ t('publish') }}

                            <template v-slot:append>
                              <v-icon
                                class="rotate-animation"
                                color="primary"
                              ></v-icon>
                            </template>
                          </v-btn>
                          <v-btn
                            append-icon="mdi-upload"
                            @click="publishPost"
                            v-else-if="!post.publish"
                          >
                            {{ t('publish') }}

                            <template v-slot:append>
                              <v-icon color="success"></v-icon>
                            </template>
                          </v-btn>
                          <v-btn
                            class="ml-3"
                            append-icon="mdi-send-variant-clock-outline"
                            @click="scheduler.schedulePost = true"
                          >
                            {{ t('schedule') }}

                            <template v-slot:append>
                              <v-icon color="primary"></v-icon>
                            </template>
                          </v-btn>
                          <v-dialog
                            v-model="scheduler.schedulePost"
                            max-width="750px"
                            class="dialog scheduler-dialog"
                          >
                            <v-card>
                              <v-card-title class="dialog-title">
                                <span class="text-h5">{{
                                  t('schedule_post')
                                }}</span>
                                <v-btn
                                  class="close-dialog"
                                  @click="scheduler.schedulePost = false"
                                >
                                  <span class="mdi mdi-close"></span>
                                </v-btn>
                              </v-card-title>

                              <v-card-text class="scheduler-schedule-container">
                                <v-date-picker
                                  elevation="24"
                                  max-width="350"
                                  class="scheduler-date-picker"
                                  :min="scheduler.minDate"
                                  v-model="scheduler.selectedDate"
                                ></v-date-picker>
                                <v-time-picker
                                  format="24hr"
                                  max-width="350"
                                  class="scheduler-time-picker"
                                  :min="scheduler.minHour"
                                  v-model="scheduler.selectedTime"
                                ></v-time-picker>
                              </v-card-text>
                              <v-card-actions>
                                <v-spacer></v-spacer>
                                <v-btn
                                  append-icon="mdi-cached"
                                  variant="tonal"
                                  color="primary"
                                  class="schedule-btn"
                                  v-if="post.schedule"
                                >
                                  {{ t('schedule') }}

                                  <template v-slot:append>
                                    <v-icon
                                      class="rotate-animation"
                                      color="primary"
                                    ></v-icon>
                                  </template>
                                </v-btn>
                                <v-btn
                                  append-icon="mdi-send-variant-clock-outline"
                                  variant="tonal"
                                  color="primary"
                                  class="schedule-btn"
                                  @click="schedulePost"
                                  v-else-if="!post.schedule"
                                >
                                  {{ t('schedule') }}

                                  <template v-slot:append>
                                    <v-icon color="primary"></v-icon>
                                  </template>
                                </v-btn>
                              </v-card-actions>
                            </v-card>
                          </v-dialog>
                        </v-col>
                      </v-row>
                    </v-form>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-row>
                      <v-col cols="12">
                        <v-card
                          class="first-preview"
                          v-if="post.text || post.image"
                        >
                          <v-card-title class="post-header">
                            <div class="post-author-cover">
                              <span class="mdi mdi-account"></span>
                            </div>
                            <h3>
                              {{ t('your_name')
                              }}<span>{{ t('just_now') }}</span>
                            </h3>
                          </v-card-title>
                          <v-card-text class="post-body">
                            {{ post.text }}
                          </v-card-text>
                          <v-img
                            class="align-end text-white"
                            height="400"
                            :src="imageUrl(post.image)"
                            cover
                            v-if="post.image"
                          >
                          </v-img>
                          <v-card-actions class="post-footer">
                            <v-row>
                              <v-col cols="4">
                                <span class="mdi mdi-thumb-up-outline"></span>
                                {{ t('like') }}
                              </v-col>
                              <v-col cols="4">
                                <span class="mdi mdi-comment-outline"></span>
                                {{ t('comment') }}
                              </v-col>
                              <v-col cols="4">
                                <span class="mdi mdi-share-variant"></span>
                                {{ t('share') }}
                              </v-col>
                            </v-row>
                          </v-card-actions>
                        </v-card>
                        <v-card class="default-preview" v-else>
                          <v-card-text>
                            <span class="mdi mdi-post-outline"></span>
                          </v-card-text>
                        </v-card>
                      </v-col>
                    </v-row>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
        <v-dialog v-model="posts.modal" max-width="600px" class="post-modal">
          <v-card>
            <v-card-text class="post-modal-body">
              <v-row>
                <v-col cols="8" class="network-accounts-list">
                  <v-btn-toggle
                    class="network-account-group mr-3"
                    v-for="network in posts.post?.networks"
                    :key="network.network.id"
                  >
                    <v-btn>
                      <v-img
                        src="/fb-blue.png"
                        width="22"
                        height="22"
                        alt="Facebook Icon"
                        class="network-icon"
                        v-if="network.network.network_name == 'facebook_pages'"
                      ></v-img>
                      <v-img
                        src="/threads.png"
                        width="22"
                        height="22"
                        alt="Threads Icon"
                        class="network-icon"
                        v-if="network.network.network_name == 'threads'"
                      ></v-img>
                      {{ network.network.name }}
                    </v-btn>
                  </v-btn-toggle>
                </v-col>
                <v-col cols="4" class="post-time">
                  <div
                    v-html="
                      calculate_time(
                        posts.post?.created_at ?? 0,
                        posts.current_time,
                      )
                    "
                  ></div>
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="12" class="post-text">
                  <p>{{ posts.post?.text ?? '' }}</p>
                </v-col>
              </v-row>
              <v-row v-if="posts.post && posts.post.image">
                <v-col cols="12" class="post-image">
                  <v-img
                    :src="imageUrl(posts.post.image)"
                    alt="Post Image"
                  ></v-img>
                </v-col>
              </v-row>
              <v-row v-if="posts.post && posts.post.scheduled">
                <v-col cols="12" class="post-actions">
                  <v-btn
                    class="post-cancel-btn"
                    color="indigo-darken-3"
                    @click="cancelScheduledPost(posts.post?.id ?? '')"
                  >
                    <span class="mdi mdi-close-circle-outline"></span>
                    {{ t('cancel') }}
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-dialog>
      </v-container>
    </v-main>
  </v-app>
</template>
<style scoped lang="scss">
@import '@/assets/styles/general/general.index';
@import '@/assets/styles/animations/animations.index';

.v-spinner {
  position: fixed;
  bottom: 0;
  left: 0;
  padding: 7px 5px 0 0;
  font-size: 10px;
  width: 60px;
  height: 30px;
  border-radius: 0 3px 0 0;
  text-align: center;
  background-color: rgba(#ffffff, 0.7);
}

.v-pulse1 {
  animation-fill-mode: both;
  animation-timing-function: cubic-bezier(0.2, 0.68, 0.18, 1.08);
  animation-iteration-count: infinite;
  animation-duration: 0.75s;
  animation-name: v-pulseStretchDelay;
  display: inline-block;
  border-radius: 100%;
  margin: 2px;
  height: 10px;
  width: 10px;
  background-color: rgb(58, 185, 130);
  animation-delay: 0.12s;
}

.v-pulse2 {
  animation-fill-mode: both;
  animation-timing-function: cubic-bezier(0.2, 0.68, 0.18, 1.08);
  animation-iteration-count: infinite;
  animation-duration: 0.75s;
  animation-name: v-pulseStretchDelay;
  display: inline-block;
  border-radius: 100%;
  margin: 2px;
  height: 10px;
  width: 10px;
  background-color: rgb(58, 185, 130);
  animation-delay: 0.24s;
}

.v-pulse3 {
  animation-fill-mode: both;
  animation-timing-function: cubic-bezier(0.2, 0.68, 0.18, 1.08);
  animation-iteration-count: infinite;
  animation-duration: 0.75s;
  animation-name: v-pulseStretchDelay;
  display: inline-block;
  border-radius: 100%;
  margin: 2px;
  height: 10px;
  width: 10px;
  background-color: rgb(58, 185, 130);
  animation-delay: 0.36s;
}

@-webkit-keyframes v-pulseStretchDelay {
  0%,
  80% {
    -webkit-transform: scale(1);
    transform: scale(1);
    -webkit-opacity: 1;
    opacity: 1;
  }
  45% {
    -webkit-transform: scale(0.1);
    transform: scale(0.1);
    -webkit-opacity: 0.7;
    opacity: 0.7;
  }
}

@keyframes v-pulseStretchDelay {
  0%,
  80% {
    -webkit-transform: scale(1);
    transform: scale(1);
    -webkit-opacity: 1;
    opacity: 1;
  }
  45% {
    -webkit-transform: scale(0.1);
    transform: scale(0.1);
    -webkit-opacity: 0.7;
    opacity: 0.7;
  }
}

.dialog {
  .dialog-title {
    display: flex;
    justify-content: space-between;
    margin-top: 10px !important;

    .text-h5 {
      font-family: $font-5;
      font-size: 20px !important;
    }

    .close-dialog {
      padding: 0 5px;
      height: 30px;
      min-width: 0;
      min-height: 0;
      font-size: 24px !important;
      background-color: transparent !important;
      box-shadow: none !important;
    }
  }
}

.scheduler-dialog {
  .scheduler-schedule-container {
    display: flex;
    justify-content: space-between;
    padding: 15px 15px !important;

    .scheduler-date-picker,
    .scheduler-time-picker {
      width: 50%;
      box-shadow: none !important;
      font-family: $font-5;
      background-color: rgba($color-blue, 0.05);
    }
  }

  .schedule-btn {
    margin: 0 7px 7px 0 !important;
  }
}

.composer-toolbar {
  height: 64px;
  box-shadow:
    0px 12px 16px -4px rgba(16, 24, 40, 0.05),
    0px 4px 6px -2px rgba(16, 24, 40, 0.03) !important;

  .v-btn {
    .mdi {
      margin-left: 5px;
      font-size: 18px;
    }
  }
}
.composer-main {
  .composer-container {
    .posts-list,
    .posts-composer {
      height: calc(100vh - 64px);
    }

    .posts-list {
      overflow-x: hidden;
      overflow-y: auto;
      height: calc(100vh - 65px);
      background-color: #d4dcff;

      &::-webkit-scrollbar {
        width: 2px;
      }

      &::-webkit-scrollbar-track {
        background: #d4dcff;
      }

      &::-webkit-scrollbar-thumb {
        border-radius: 5px;
        background: $color-grey;
      }

      &::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.1);
      }

      .no-posts {
        padding: 10px 15px;
        font-family: $font-5;
        font-size: 14px;
        font-weight: 400;
        background-color: rgba(#ffffff, 0.2);
        color: $color-black;
      }

      .post-card {
        margin-bottom: 15px;
        padding: 10px !important;
        border: 1px solid #4f518c;
        border-radius: 6px;
        background-color: #ffffff !important;
        box-shadow: none !important;

        .post-card-title {
          display: flex;
          justify-content: space-between;
          margin-top: -2px;
          margin-bottom: 15px;
          padding: 0 !important;

          & > span {
            margin-bottom: 5px;
            padding: 5px 10px;
            font-family: $font-5;
            font-size: 13px;
            font-weight: 400;

            &.post-status-failed {
              background-color: rgba($color-red, 0.3) !important;
              color: $color-black !important;
            }

            &.post-status-published {
              background-color: rgba($color-green, 0.3) !important;
              color: $color-black !important;
            }

            &.post-status-scheduled {
              background-color: rgba($color-blue, 0.2) !important;
              color: $color-black !important;
            }
          }

          & > small {
            margin-top: 5px;
            font-family: $font-5;
            font-size: 13px;
            font-weight: 400;
            color: $color-black !important;
          }
        }

        .post-card-text {
          display: -webkit-box;
          padding: 0 !important;
          overflow: hidden;
          line-height: 25px;
          text-overflow: ellipsis;
          text-align: left;
          font-family: $font-7;
          color: #16102a !important;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
        }

        .post-card-button {
          margin-top: 15px;
        }

        .post-card-actions {
          padding: 0 !important;

          .v-btn {
            padding: 5px;
            height: fit-content;
            min-width: fit-content;
            font-size: 24px;
            color: $color-green !important;
          }
        }
      }
    }

    .posts-composer {
      padding: 25px 0;
      background-color: rgba(#2c2a4a, 1);

      .post-profile {
        margin: 0 15px;
        width: 60px;
        height: 83.5px;

        &:first-child {
          margin-left: 0;
        }

        label {
          position: relative;
          cursor: pointer;

          img {
            border-radius: 50%;
          }

          .mdi {
            position: absolute;
            width: 100%;
            height: 60px;
            border-radius: 50%;
            line-height: 60px;
            text-align: center;
            font-size: 24px;
            background-color: transparent;
            color: transparent;
            transition: all 0.3s ease-in-out;
          }

          small {
            display: block;
            overflow: hidden;
            width: 60px;
            white-space: nowrap;
            text-overflow: ellipsis;
            text-align: center;
            font-family: $font-1;
            font-size: 11px;
            color: rgba(#ffffff, 0.8);
            transition: all 0.3s ease-in-out;
          }
          .cover {
            display: block;
            margin-bottom: 5px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            line-height: 60px;
            text-align: center;
            &.cover-fb {
              color: #ffffff;
              background-color: #4267b2;
            }
            &.cover-threads {
              color: #000000;
              background-color: #ffffff;
            }
          }
        }

        input[type='checkbox'] {
          display: none;
        }

        input[type='checkbox']:checked + label > .mdi {
          background-color: rgba(#ffffff, 0.2);
          color: $color-yellow;
        }

        input[type='checkbox']:checked + label > small {
          color: $color-yellow;
        }
      }

      .accounts-menu-btn {
        margin: 0;
        width: 83.5px;
        height: 83.5px;
        border: 1px solid rgba(#ffffff, 0.2);
        border-radius: 12px;
        background-color: transparent !important;

        .mdi {
          font-size: 40px;
          color: rgba(#ffffff, 0.8);
        }
      }

      .composer {
        .composer-textarea {
          .v-label {
            font-family: $font-1;
            font-size: 14px;
          }
        }
      }

      .composer-image {
        padding-left: 15px;
        padding-right: 15px;
        border-radius: 12px;
        font-family: $font-6 !important;
        font-size: 16px;
        background-color: rgba(#ffffff, 0.1);
        color: #ffffff !important;
      }

      .default-preview {
        text-align: center;

        .mdi {
          font-size: 272px;
          color: rgba($color-blue, 0.1);
        }
      }

      .first-preview {
        .post-header {
          display: flex;
          padding: 15px;

          .post-author-cover {
            width: 40px;
            height: 40px;
            text-align: center;
            line-height: 40px;
            font-size: 28px;
            background-color: rgba($color-blue, 0.1);
            color: rgba($color-blue, 1);
          }

          h3 {
            padding: 2px 15px;
            font-family: $font-1;
            font-size: 13px;
            color: $color-black;

            span {
              display: block;
              margin-top: -5px;
              font-family: $font-1;
              font-size: 12px;
              font-weight: 400;
              color: $color-grey;
            }
          }
        }

        .post-body {
          padding: 0 15px 15px;
          border-bottom: 1px solid rgba($color-blue, 0.2);
        }

        .post-footer {
          line-height: 40px;
          text-align: center;
          font-family: $font-5;
          font-size: 14px;

          .mdi {
            display: inline-block;
            vertical-align: middle;
            margin-top: -3px;
            margin-right: 5px;
            font-size: 18px;
            font-weight: 400;
          }
        }
      }
    }
  }
}

.accounts-menu-popover {
  margin: 0 15px !important;

  .social-list {
    width: 340px;

    .social-list-tabs {
      width: 48px;
      height: 350px;
      background-color: rgba($color-blue, 0.02);

      button {
        padding-left: 14px;
        width: 48px !important;
        min-width: 48px !important;
      }
    }

    .v-tabs-window {
      width: 100%;

      .v-tabs-window-item {
        .facebook-network-btn {
          width: 100%;
          text-transform: inherit;
          font-family: Arial, sans-serif;
          font-size: 13px;
          font-weight: 600;
          background-color: #1877f2 !important;
          color: #ffffff;
          box-shadow: none;
        }

        .threads-network-btn {
          width: 100%;
          text-transform: inherit;
          font-family: Arial, sans-serif;
          font-size: 13px;
          font-weight: 600;
          background-color: #000000 !important;
          color: #ffffff;
          box-shadow: none;
        }

        .network-accounts-list {
          overflow-x: hidden;
          overflow-y: auto;
          max-height: 250px;

          &::-webkit-scrollbar {
            width: 2px;
          }

          &::-webkit-scrollbar-track {
            background: transparent;
          }

          &::-webkit-scrollbar-thumb {
            border-radius: 5px;
            background: $color-blue;
          }

          &::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.1);
          }

          .network-account-group {
            button {
              padding: 0 10px;
              height: 30px !important;
              text-transform: inherit;
              font-family: $font-2;
              font-size: 12px;
              font-weight: 400;
              background-color: $color-grey !important;
              color: #ffffff;

              & > span {
                overflow: hidden;
                width: 50px;
                white-space: nowrap;
                text-overflow: ellipsis;
              }

              &:last-child {
                padding: 0 8px;
                min-width: fit-content;
              }

              .mdi {
                font-size: 18px;
              }
            }

            &:has(.selected-account) {
              button {
                background-color: #40798c !important;
              }
            }
          }
        }

        .network-accounts-no-list {
          max-height: 250px;

          p {
            font-family: $font-1;
            font-size: 13px;
            font-weight: 400;
            color: $color-black;
          }
        }
      }
    }
  }
}
.post-modal {
  .post-modal-body {
    overflow-x: hidden;
    overflow-y: auto;
    padding: 15px;
    max-height: 500px;

    &::-webkit-scrollbar {
      width: 2px;
    }

    &::-webkit-scrollbar-track {
      background: transparent;
    }

    &::-webkit-scrollbar-thumb {
      border-radius: 5px;
      background: $color-blue;
    }

    &::-webkit-scrollbar-thumb:hover {
      background: rgba(255, 255, 255, 0.1);
    }

    .network-accounts-list {
      padding: 15px 0 0;

      .network-account-group {
        button {
          padding: 0 15px !important;
          height: 33px !important;
          border: 1px solid $color-grey !important;
          text-transform: inherit;
          font-family: $font-2;
          font-size: 12px;
          font-weight: 400;
          background-color: transparent !important;
          color: $color-black;
          pointer-events: none;

          &.v-btn__overlay {
            background-color: transparent !important;
          }

          & > span {
            overflow: hidden;
            width: 50px;
            white-space: nowrap;
            text-overflow: ellipsis;

            .network-icon {
              margin-right: 5px;
              max-width: 17px;
            }
          }
        }
      }
    }

    .network-accounts-no-list {
      max-height: 250px;

      p {
        font-family: $font-1;
        font-size: 13px;
        font-weight: 400;
        color: $color-black;
      }
    }

    .post-time {
      padding-right: 0;
      line-height: 39px;
      text-align: right;
      font-family: $font-1;
      font-size: 13px;
      font-weight: 400;
      color: $color-black;
    }

    .post-text {
      border-top: 1px solid rgba($color-grey, 0.2) !important;

      p {
        font-family: $font-7;
        font-size: 13px;
        font-weight: 400;
        color: $color-black;
      }
    }

    .post-image {
      img {
        max-width: 100%;
      }
    }

    .post-actions {
      padding-right: 0;
      border-top: 1px solid rgba($color-grey, 0.2) !important;
      text-align: right;

      .post-cancel-btn {
        .mdi {
          margin: 0 5px 0 0;
          font-size: 22px;
        }
      }
    }
  }
}
</style>
