import { configureStore } from '@reduxjs/toolkit';
import authReducer from './auth';
import cameraReducer from './cameras';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    cameras: cameraReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 