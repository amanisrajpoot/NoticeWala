/**
 * NoticeWala Main App Component
 */

import React, { useEffect } from 'react';
import { StatusBar } from 'react-native';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { NavigationContainer } from '@react-navigation/native';
import { PaperProvider } from 'react-native-paper';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { store, persistor } from '@store/index';
import AppNavigator from '@navigation/AppNavigator';
import { theme } from '@utils/theme';
import { initializePushNotifications } from '@services/notificationService';

const App: React.FC = () => {
  useEffect(() => {
    // Initialize push notifications
    initializePushNotifications();
  }, []);

  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <SafeAreaProvider>
          <PaperProvider theme={theme}>
            <NavigationContainer>
              <StatusBar
                barStyle="dark-content"
                backgroundColor="#ffffff"
                translucent={false}
              />
              <AppNavigator />
            </NavigationContainer>
          </PaperProvider>
        </SafeAreaProvider>
      </PersistGate>
    </Provider>
  );
};

export default App;
