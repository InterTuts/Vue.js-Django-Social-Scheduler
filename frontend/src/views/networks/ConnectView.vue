<script setup lang="ts">
// System Utils
import { ref, onMounted } from 'vue';

// Installed Utils
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useHead } from '@vueuse/head';

// App Utils
import axios, { type AxiosResponse } from '@/axios';
import type ApiResponse from '@/interfaces/apiResponse';

// Get i18n functions
const { t } = useI18n();

// Use the router
const router = useRouter();

// Error messages reactive var
const errorMessage = ref('');

// Set page title and description
useHead({
  title: t('connect_account'),
  meta: [
    {
      name: 'description',
      content: () => t('connect_account_page_description'),
    },
    { name: 'keywords', content: () => 'connect, social, account, network' },
  ],
});

// Wait until the component is mounted
onMounted(async () => {
  // Get the network
  const network = router.currentRoute.value.params.network;

  try {
    // Send request
    const response: AxiosResponse<ApiResponse<string>> = await axios.get(
      'api/networks/connect/' + network,
    );

    // Check if the message is success
    if (response.data.success) {
      document.location.href = response.data.content ?? '';
      // Wait until the message is showed
      setTimeout(function () {
        // Verify if opener exists
        if (window.opener) {
          // Reload accounts
          window.opener.reloadAccounts();
        }

        // Close modal
        window.close();
      }, 1500);
    } else {
      errorMessage.value = response.data.message;
    }
  } catch (error) {
    console.error(error);
  }
});
</script>
<template>
  <v-app>
    <v-main>
      <v-container>
        <v-row>
          <v-col cols="12">
            <div class="networks-form-alerts">
              <div
                class="networks-form-alert-error top-to-bottom-animation"
                role="alert"
                v-if="errorMessage"
              >
                <span
                  class="mdi mdi-bell-outline networks-form-alert-error-icon"
                ></span>
                <p>{{ errorMessage }}</p>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>
<style scoped lang="scss">
@import '@/assets/styles/general/general.index';
.networks-form-alerts {
  .networks-form-alert-success,
  .networks-form-alert-error {
    display: flex;
    padding: 10px 15px;
    width: 100%;
    line-height: 24px;
    font-family: $font-7;
    font-size: 14px;
    font-weight: 400;

    .networks-form-alert-success-icon,
    .networks-form-alert-error-icon {
      display: inline-block;
      margin-right: 5px;
      font-size: 24px;
    }

    p {
      display: inline-block;
    }
  }

  .networks-form-alert-success {
    background-color: rgba($color: $color-blue, $alpha: 0.2);
    color: $color-blue;

    .networks-form-alert-success-icon {
      color: $color-blue;
    }
  }

  .networks-form-alert-error {
    background-color: rgba($color: $color-red, $alpha: 0.2);
    color: $color-red;

    .networks-form-alert-error-icon {
      color: $color-red;
    }
  }
}
</style>
