import api from './api';

export const authApi = {
  /**
   * Sign up a new farmer
   * @param {{ name, phone, email?, pin_code, land_area, land_unit }} data
   */
  signup(data) {
    return api.post('/auth/signup', data);
  },

  /**
   * Verify OTP (phone or email)
   * @param {{ phone, otp, type: 'phone'|'email' }} data
   */
  verifyOtp(data) {
    return api.post('/auth/verify-otp', data);
  },

  /**
   * Request login OTP
   * @param {{ phone }} data
   */
  login(data) {
    return api.post('/auth/login', data);
  },

  /**
   * Verify login OTP — returns tokens
   * @param {{ phone, otp }} data
   */
  loginVerify(data) {
    return api.post('/auth/login/verify', data);
  },

  /**
   * Refresh access token
   * @param {{ refresh_token }} data
   */
  refresh(data) {
    return api.post('/auth/refresh', data);
  },

  /**
   * Logout
   */
  logout() {
    return api.post('/auth/logout');
  },
};
