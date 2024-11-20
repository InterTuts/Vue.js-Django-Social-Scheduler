// System Utils
import { h } from 'vue';

// Installed Utils
import { mount, VueWrapper } from '@vue/test-utils';
import { vi, describe, it, expect, beforeAll, afterAll } from 'vitest';
import { VApp } from 'vuetify/components';

// App Utils
import SignInView from '../SignInView.vue';
import { useAuth } from '@/composables/useAuth';
import axios, { type Axios } from '@/axios';

// Create a mock for axios
vi.mock('axios', async () => {
  const actual = await vi.importActual<typeof Axios>('axios');
  return {
    ...actual,
  };
});

describe('SignInForm.vue', () => {
  let wrapper: VueWrapper;

  beforeAll(() => {
    wrapper = mount(VApp, {
      slots: {
        default: h(SignInView),
      },
    });
  });

  afterAll(() => {
    wrapper.unmount();
  });

  it('renders the strings correctly', () => {
    expect(wrapper.text()).toContain('Sign In to MyApp');
    expect(wrapper.text()).toContain('Continue with Google');
    expect(wrapper.text()).toContain('Forgot Password?');
    expect(wrapper.text()).toContain("Don't have an account?");
    expect(wrapper.text()).toContain('Register an account');
  });

  it('renders the vuetify inputs', () => {
    const emailInput = wrapper.find('input[type="email"]');
    const passwordInput = wrapper.find('input[type="password"]');
    expect(emailInput.exists()).toBeTruthy();
    expect(passwordInput.exists()).toBeTruthy();
  });

  it('validates form fields', async () => {
    const emailInput = wrapper.find('input[type="email"]');
    const passwordInput = wrapper.find('input[type="password"]');
    await emailInput.setValue('invalid email');
    await passwordInput.setValue('short');
    await wrapper.find('form').trigger('submit.prevent');
    expect(wrapper.text()).toContain('The email address is not valid.');
    expect(wrapper.text()).toContain('The password is too short.');
  });

  it('sends login request', async () => {
    // Create a mock response
    const mockResponse = {
      data: { success: true, content: {}, message: 'Success' },
    };

    // Set the mock response as axios response
    const mockAxiosPost = vi.fn().mockResolvedValue(mockResponse);

    // Replace the axios.post function with the mock
    axios.post = mockAxiosPost;

    // Arrange
    const { authRequest, successMessage, errorMessage, isLoading } = useAuth();

    // Try to login
    const response = await authRequest('api/auth/sign-in', {
      email: 'test@example.com',
      password: 'test',
    });

    // Verify if the response has expected values
    expect(isLoading.value).toBe(false);
    expect(successMessage.value).toBe('Success');
    expect(errorMessage.value).toBe('');
    expect(response).toEqual(mockResponse.data);
  });
});
