/**
 * UI Preferences Component
 * Configure user interface customization and display preferences
 */

import React from 'react';
import { useSettingsStore } from '@/lib/settings-store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export function UIPreferences() {
  const { settings, updateUIPreferences } = useSettingsStore();
  const { ui } = settings;

  const handleToggle = (field: keyof typeof ui) => {
    updateUIPreferences({ [field]: !ui[field] });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">UI Preferences</h2>
        <p className="text-muted-foreground">
          Customize the user interface to match your preferences
        </p>
      </div>

      {/* Appearance */}
      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>
            Customize the visual appearance of the application
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Theme */}
          <div className="space-y-2">
            <Label htmlFor="theme">Color Theme</Label>
            <Select
              value={ui.theme}
              onValueChange={(value: typeof ui.theme) =>
                updateUIPreferences({ theme: value })
              }
            >
              <SelectTrigger id="theme">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="light">Light</SelectItem>
                <SelectItem value="dark">Dark</SelectItem>
                <SelectItem value="system">System</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              Choose your preferred color theme or sync with system settings
            </p>
          </div>

          {/* Animations */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="animations">Enable Animations</Label>
              <p className="text-sm text-muted-foreground">
                Show smooth transitions and animations
              </p>
            </div>
            <Switch
              id="animations"
              checked={ui.animationsEnabled}
              onCheckedChange={() => handleToggle('animationsEnabled')}
            />
          </div>

          {/* Compact Mode */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="compactMode">Compact Mode</Label>
              <p className="text-sm text-muted-foreground">
                Reduce spacing and padding for denser information display
              </p>
            </div>
            <Switch
              id="compactMode"
              checked={ui.compactMode}
              onCheckedChange={() => handleToggle('compactMode')}
            />
          </div>
        </CardContent>
      </Card>

      {/* Layout */}
      <Card>
        <CardHeader>
          <CardTitle>Layout</CardTitle>
          <CardDescription>
            Configure dashboard layout and navigation
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Dashboard Layout */}
          <div className="space-y-2">
            <Label htmlFor="dashboardLayout">Dashboard Layout</Label>
            <Select
              value={ui.dashboardLayout}
              onValueChange={(value: typeof ui.dashboardLayout) =>
                updateUIPreferences({ dashboardLayout: value })
              }
            >
              <SelectTrigger id="dashboardLayout">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="sidebar">Sidebar Navigation</SelectItem>
                <SelectItem value="topbar">Top Bar Navigation</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              Choose your preferred navigation layout
            </p>
          </div>

          {/* Default View */}
          <div className="space-y-2">
            <Label htmlFor="defaultView">Default View</Label>
            <Select
              value={ui.defaultView}
              onValueChange={(value: typeof ui.defaultView) =>
                updateUIPreferences({ defaultView: value })
              }
            >
              <SelectTrigger id="defaultView">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="dashboard">Dashboard</SelectItem>
                <SelectItem value="pipeline">Pipeline Monitor</SelectItem>
                <SelectItem value="settings">Settings</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              Page to display when opening the application
            </p>
          </div>

          {/* Show Advanced Options */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="advancedOptions">Show Advanced Options</Label>
              <p className="text-sm text-muted-foreground">
                Display advanced configuration options throughout the UI
              </p>
            </div>
            <Switch
              id="advancedOptions"
              checked={ui.showAdvancedOptions}
              onCheckedChange={() => handleToggle('showAdvancedOptions')}
            />
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
          <CardDescription>
            Configure notification and sound preferences
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Enable Notifications */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="notifications">Enable Notifications</Label>
              <p className="text-sm text-muted-foreground">
                Show desktop notifications for important events
              </p>
            </div>
            <Switch
              id="notifications"
              checked={ui.notifications}
              onCheckedChange={() => handleToggle('notifications')}
            />
          </div>

          {/* Sound Effects */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="soundEffects">Sound Effects</Label>
              <p className="text-sm text-muted-foreground">
                Play sounds for notifications and events
              </p>
            </div>
            <Switch
              id="soundEffects"
              checked={ui.soundEffects}
              onCheckedChange={() => handleToggle('soundEffects')}
            />
          </div>
        </CardContent>
      </Card>

      {/* Preview */}
      <Card>
        <CardHeader>
          <CardTitle>Current Configuration</CardTitle>
          <CardDescription>
            Preview of your current UI settings
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Theme</p>
              <p className="text-lg font-semibold capitalize">{ui.theme}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Layout</p>
              <p className="text-lg font-semibold capitalize">
                {ui.dashboardLayout === 'sidebar' ? 'Sidebar' : 'Top Bar'}
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Default View</p>
              <p className="text-lg font-semibold capitalize">{ui.defaultView}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Features</p>
              <p className="text-lg font-semibold">
                {[
                  ui.notifications && 'Notifications',
                  ui.animationsEnabled && 'Animations',
                  ui.compactMode && 'Compact',
                ]
                  .filter(Boolean)
                  .join(', ') || 'None'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
