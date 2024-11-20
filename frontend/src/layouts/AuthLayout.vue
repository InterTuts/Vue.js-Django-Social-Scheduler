<template>
  <v-app class="auth-layout">
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>
<style lang="scss">
@import '@/assets/styles/auth/_main.scss';
.auth-layout {
  &.v-application {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #274384;
  }
}
</style>
