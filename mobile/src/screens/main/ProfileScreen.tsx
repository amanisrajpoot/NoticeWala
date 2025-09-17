/**
 * Profile Screen for NoticeWala Mobile App
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import {
  Text,
  Card,
  Button,
  List,
  Switch,
  Avatar,
  Divider,
  TextInput,
  Dialog,
  Portal,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '@store/hooks';
import { logoutUser, updateProfile } from '@store/slices/authSlice';
import { colors, spacing, borderRadius, typography } from '@utils/theme';

const ProfileScreen: React.FC = () => {
  const navigation = useNavigation();
  const dispatch = useAppDispatch();
  
  const { user, isLoading } = useAppSelector((state) => state.auth);
  
  const [isEditMode, setIsEditMode] = useState(false);
  const [editData, setEditData] = useState({
    first_name: '',
    last_name: '',
    username: '',
  });
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [logoutDialogVisible, setLogoutDialogVisible] = useState(false);

  useEffect(() => {
    if (user) {
      setEditData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        username: user.username || '',
      });
    }
  }, [user]);

  const handleEditProfile = () => {
    setIsEditMode(true);
  };

  const handleSaveProfile = async () => {
    try {
      await dispatch(updateProfile(editData)).unwrap();
      setIsEditMode(false);
      Alert.alert('Success', 'Profile updated successfully');
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to update profile');
    }
  };

  const handleCancelEdit = () => {
    if (user) {
      setEditData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        username: user.username || '',
      });
    }
    setIsEditMode(false);
  };

  const handleLogout = () => {
    setLogoutDialogVisible(true);
  };

  const confirmLogout = async () => {
    setLogoutDialogVisible(false);
    try {
      await dispatch(logoutUser()).unwrap();
    } catch (error) {
      Alert.alert('Error', 'Failed to logout');
    }
  };

  const getInitials = (firstName?: string, lastName?: string) => {
    const first = firstName?.charAt(0) || '';
    const last = lastName?.charAt(0) || '';
    return (first + last).toUpperCase();
  };

  const getDisplayName = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    return user?.username || user?.email || 'User';
  };

  if (!user) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>User not found</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Profile Header */}
        <Card style={styles.profileCard}>
          <Card.Content style={styles.profileContent}>
            <View style={styles.profileHeader}>
              <Avatar.Text
                size={80}
                label={getInitials(user.first_name, user.last_name)}
                style={styles.avatar}
              />
              <View style={styles.profileInfo}>
                <Text style={styles.displayName}>{getDisplayName()}</Text>
                <Text style={styles.email}>{user.email}</Text>
                {user.created_at && (
                  <Text style={styles.memberSince}>
                    Member since {new Date(user.created_at).toLocaleDateString()}
                  </Text>
                )}
              </View>
            </View>
            
            {isEditMode ? (
              <View style={styles.editActions}>
                <Button
                  mode="outlined"
                  onPress={handleCancelEdit}
                  style={styles.editButton}
                >
                  Cancel
                </Button>
                <Button
                  mode="contained"
                  onPress={handleSaveProfile}
                  loading={isLoading}
                  disabled={isLoading}
                  style={styles.editButton}
                >
                  Save
                </Button>
              </View>
            ) : (
              <Button
                mode="outlined"
                onPress={handleEditProfile}
                style={styles.editButton}
              >
                Edit Profile
              </Button>
            )}
          </Card.Content>
        </Card>

        {/* Edit Profile Form */}
        {isEditMode && (
          <Card style={styles.editCard}>
            <Card.Content>
              <Text style={styles.sectionTitle}>Profile Information</Text>
              
              <View style={styles.inputRow}>
                <TextInput
                  label="First Name"
                  value={editData.first_name}
                  onChangeText={(text) => setEditData(prev => ({ ...prev, first_name: text }))}
                  style={styles.halfInput}
                  mode="outlined"
                />
                <TextInput
                  label="Last Name"
                  value={editData.last_name}
                  onChangeText={(text) => setEditData(prev => ({ ...prev, last_name: text }))}
                  style={styles.halfInput}
                  mode="outlined"
                />
              </View>
              
              <TextInput
                label="Username"
                value={editData.username}
                onChangeText={(text) => setEditData(prev => ({ ...prev, username: text }))}
                style={styles.input}
                mode="outlined"
                autoCapitalize="none"
              />
            </Card.Content>
          </Card>
        )}

        {/* Settings */}
        <Card style={styles.settingsCard}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Settings</Text>
            
            <List.Item
              title="Push Notifications"
              description="Receive notifications about new announcements"
              left={(props) => <List.Icon {...props} icon="bell" />}
              right={() => (
                <Switch
                  value={notificationsEnabled}
                  onValueChange={setNotificationsEnabled}
                />
              )}
            />
            
            <Divider />
            
            <List.Item
              title="Manage Subscriptions"
              description="View and edit your notification subscriptions"
              left={(props) => <List.Icon {...props} icon="bookmark" />}
              right={(props) => <List.Icon {...props} icon="chevron-right" />}
              onPress={() => navigation.navigate('Subscription' as never)}
            />
            
            <Divider />
            
            <List.Item
              title="Privacy Policy"
              description="Read our privacy policy"
              left={(props) => <List.Icon {...props} icon="shield" />}
              right={(props) => <List.Icon {...props} icon="chevron-right" />}
              onPress={() => Alert.alert('Privacy Policy', 'Privacy policy will be available soon.')}
            />
            
            <Divider />
            
            <List.Item
              title="Terms of Service"
              description="Read our terms of service"
              left={(props) => <List.Icon {...props} icon="file-document" />}
              right={(props) => <List.Icon {...props} icon="chevron-right" />}
              onPress={() => Alert.alert('Terms of Service', 'Terms of service will be available soon.')}
            />
            
            <Divider />
            
            <List.Item
              title="Help & Support"
              description="Get help and contact support"
              left={(props) => <List.Icon {...props} icon="help-circle" />}
              right={(props) => <List.Icon {...props} icon="chevron-right" />}
              onPress={() => Alert.alert('Help & Support', 'Support will be available soon.')}
            />
          </Card.Content>
        </Card>

        {/* Account Actions */}
        <Card style={styles.actionsCard}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Account</Text>
            
            <Button
              mode="outlined"
              onPress={handleLogout}
              style={styles.logoutButton}
              textColor={colors.error}
              icon="logout"
            >
              Sign Out
            </Button>
          </Card.Content>
        </Card>

        {/* App Info */}
        <Card style={styles.infoCard}>
          <Card.Content>
            <Text style={styles.appName}>NoticeWala</Text>
            <Text style={styles.appVersion}>Version 1.0.0</Text>
            <Text style={styles.appDescription}>
              Your trusted companion for exam notifications
            </Text>
          </Card.Content>
        </Card>
      </ScrollView>

      {/* Logout Confirmation Dialog */}
      <Portal>
        <Dialog visible={logoutDialogVisible} onDismiss={() => setLogoutDialogVisible(false)}>
          <Dialog.Title>Sign Out</Dialog.Title>
          <Dialog.Content>
            <Text>Are you sure you want to sign out?</Text>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setLogoutDialogVisible(false)}>Cancel</Button>
            <Button onPress={confirmLogout} textColor={colors.error}>Sign Out</Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollContent: {
    padding: spacing.md,
  },
  profileCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
  },
  profileContent: {
    padding: spacing.lg,
  },
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  avatar: {
    backgroundColor: colors.primary,
    marginRight: spacing.md,
  },
  profileInfo: {
    flex: 1,
  },
  displayName: {
    ...typography.h5,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  email: {
    ...typography.body1,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  memberSince: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  editButton: {
    borderRadius: borderRadius.md,
  },
  editActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  editCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
  },
  sectionTitle: {
    ...typography.h6,
    color: colors.text,
    marginBottom: spacing.md,
  },
  inputRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  halfInput: {
    flex: 0.48,
  },
  input: {
    marginBottom: spacing.md,
  },
  settingsCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
  },
  actionsCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
  },
  logoutButton: {
    borderColor: colors.error,
  },
  infoCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
  },
  appName: {
    ...typography.h6,
    color: colors.primary,
    textAlign: 'center',
    marginBottom: spacing.xs,
  },
  appVersion: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  appDescription: {
    ...typography.body2,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    ...typography.h6,
    color: colors.error,
  },
});

export default ProfileScreen;
