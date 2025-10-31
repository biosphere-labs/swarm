/**
 * Settings Page
 * Next.js page for the settings panel
 */

'use client';

import React from 'react';
import { SettingsPanel } from '@/components/SettingsPanel';

export default function SettingsPage() {
  return (
    <div className="min-h-screen bg-background">
      <SettingsPanel />
    </div>
  );
}
