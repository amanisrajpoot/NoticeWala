import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { Provider as PaperProvider } from 'react-native-paper';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import AppNavigator from './navigation/AppNavigator';
import { theme } from './utils/theme';

const App: React.FC = () => {
  return (
    <Router>
      <SafeAreaProvider>
        <PaperProvider theme={theme}>
          <div style={{ 
            height: '100vh', 
            width: '100vw',
            backgroundColor: '#f5f5f5',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <AppNavigator />
          </div>
        </PaperProvider>
      </SafeAreaProvider>
    </Router>
  );
};

export default App;
